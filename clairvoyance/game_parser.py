import numpy as np
from clairvoyance.champ_utils import idx_rid_dict as champ_dict
from clairvoyance.champ_utils import idx_name_dict
from clairvoyance.champ_utils import name_rid_dict
from clairvoyance.riot_api_helpers import *
from clairvoyance.config import key

def parse_game(timeline, match):
    # blue win = 0, red win = 1
    winner = int(match['teams'][0]['win'] == 'Fail')    # winner
    # always 10 champions so hard coding that 
    # get riot's champ id
    champ_list = [match['participants'][i]['championId'] for i in range(10)]

    # encode riot champ id to alphabetical order
    game = [champ_dict[f'{champ}'] for champ in champ_list]

    # make 5 hot array for both teams
    five_hot1 = np.zeros((len(champ_dict),), dtype=int)
    for j in game[0:5]:
        five_hot1[j] = 1
    five_hot2 = np.zeros((len(champ_dict),), dtype=int)
    for k in game[5:10]:
        five_hot2[k] = 1
    champs = np.concatenate((five_hot1, five_hot2))    # champion list features

    # initializing features:

    # blue kills, red kills
    bk, rk = 0, 0
    # blue/red tower count
    bt, rt = 11, 11
    # blue/red inhib count
    #   when they respawn the count should update
    bi, ri = 3, 3
    # blue/red monster kills, [air, earth, fire, water, elder, herald, baron] (repeated twice)
    #   for elder and baron, it will be a toggle, toggling to 1 on kill and back to 0 when timer runs out
    brmk = [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]]
    # team gold
    bg, rg = None, None
    # team xp
    bxp, rxp = None, None

    # tracking variables (should probably do the same for herald but thats scuffed)
    # elder lasts 150 000 (150 seconds), baron lasts 180 000 (180 seconds)
    elder_kill_time, baron_kill_time = None, None

    # inhibitors last 300 000 when killed (5 minutes)
    # false indicates not killed (or respawned), otherwise will be a timer
    bi_kill_time, ri_kill_time = [False, False, False], [False, False, False]

    data = []
    y = []
    # loop through each frame
    for f_idx in range(len(timeline['frames'])):

        timestamp = timeline['frames'][f_idx]['timestamp']

        # check if elder or baron has run out
        # elder:
        if brmk[0][4] or brmk[1][4]:
            if elder_kill_time is not None and timestamp - elder_kill_time >= 150000:
                brmk[0][4] = 0
                brmk[1][4] = 0
        # baron:
        if brmk[0][6] or brmk[1][6]:
            if baron_kill_time is not None and timestamp - baron_kill_time >= 180000:
                brmk[0][6] = 0
                brmk[1][6] = 0

        # check if inhib respawned
        # inhibs respawn in 5 minutes, 300,000
        if sum(bi_kill_time) > 0:
            for i,t in enumerate(bi_kill_time):
                if t == False:
                    break
                if timestamp - t >= 300000:
                    bi += 1
                    bi_kill_time[i] = False
        
        if sum(ri_kill_time) > 0:
            for i,t in enumerate(ri_kill_time):
                if t == False:
                    break
                if timestamp - t >= 300000:
                    ri += 1
                    ri_kill_time[i] = False

        # loop through each event
        for e_idx in range(len(timeline['frames'][f_idx]['events'])):
            event_type = timeline['frames'][f_idx]['events'][e_idx]['type']
            
            if event_type == 'CHAMPION_KILL':
                killer = timeline['frames'][f_idx]['events'][e_idx]['killerId']
                # blue team killed, so blue kills + 1 and red death + 1
                if killer <= 5:
                    bk += 1
                else:
                    rk += 1

            elif event_type == 'BUILDING_KILL':
                building_type = timeline['frames'][f_idx]['events'][e_idx]['buildingType']
                if building_type == 'TOWER_BUILDING':
                    if timeline['frames'][f_idx]['events'][e_idx]['teamId'] == 100: # 100 = blue team
                        bt -= 1
                    else:
                        rt -= 1
                elif building_type == 'INHIBITOR_BUILDING':
                    if timeline['frames'][f_idx]['events'][e_idx]['teamId'] == 100: # 100 = blue team
                        bi -= 1
                        bi_kill_time[bi_kill_time.index(False)] = timestamp
                    else:
                        ri -= 1
                        ri_kill_time[ri_kill_time.index(False)] = timestamp

            elif event_type == 'ELITE_MONSTER_KILL':
                monster_type = timeline['frames'][f_idx]['events'][e_idx]['monsterType']
                killer = timeline['frames'][f_idx]['events'][e_idx]['killerId']
                if killer <= 5:
                    t_idx = 0
                else:
                    t_idx = 1
                
                if monster_type == 'DRAGON':
                    dragon_type = timeline['frames'][f_idx]['events'][e_idx]['monsterSubType']
                    if dragon_type == 'AIR_DRAGON':
                        brmk[t_idx][0] += 1
                    elif dragon_type == 'EARTH_DRAGON':
                        brmk[t_idx][1] += 1
                    elif dragon_type == 'FIRE_DRAGON':
                        brmk[t_idx][2] += 1
                    elif dragon_type == 'WATER_DRAGON':
                        brmk[t_idx][3] += 1
                    elif dragon_type == 'ELDER_DRAGON':
                        brmk[t_idx][4] = 1
                        elder_kill_time = timeline['frames'][f_idx]['events'][e_idx]['timestamp']
                
                elif monster_type == 'RIFTHERALD':
                    if timeline['frames'][f_idx]['events'][e_idx]['killerId'] != 0:
                        brmk[t_idx][5] += 1
                
                elif monster_type == 'BARON_NASHOR':
                    brmk[t_idx][6] = 1
                    baron_kill_time = timeline['frames'][f_idx]['events'][e_idx]['timestamp']
        # done checking events

        # cum (lol!) gold and xp values
        bg, rg = 0,0
        bxp, rxp = 0,0
        for player in timeline['frames'][f_idx]['participantFrames']:
            if int(player) <= 5:
                bg += timeline['frames'][f_idx]['participantFrames'][player]['totalGold']
                bxp += timeline['frames'][f_idx]['participantFrames'][player]['xp']
            else:
                rg += timeline['frames'][f_idx]['participantFrames'][player]['totalGold']
                rxp += timeline['frames'][f_idx]['participantFrames'][player]['xp']
        '''
        data architecture:
            time        (1)
            champions   (304 @ seraphine release)
            total gold  (2)
            total exp   (2)
            blue kills  (1)
            red kills   (1)
            blue towers (1)
            red towers  (1)
            blue monster(7) [air, earth, fire, water, elder, herald, baron]
            red monster (7)
        '''

        frame = [timestamp/2400000]         # normalize by 40 minutes
        frame.extend(champs)
        frame.extend([bg/100000])
        frame.extend([rg/100000])
        frame.extend([bxp/91800])            # 18360 for lvl 18, 18360*5 = 91800
        frame.extend([rxp/91800])
        frame.extend([bk/50])                # 50 sounds like a normal kill count at the end of the game?
        frame.extend([rk/50])
        frame.extend([bt/11])
        frame.extend([rt/11])
        frame.extend([bi/3])
        frame.extend([ri/3])
        frame.extend(brmk[0])
        frame.extend(brmk[1])

        data.append(frame)
        y.append(winner)
    return data, y

def get_game_data(matchId):
    timeline = get_timeline(key, matchId).json()
    match = get_match(key, matchId).json()
    game, _ = parse_game(timeline, match)

    return np.array(game)

def custom_game(timestamp, champions, blue_gold, red_gold, blue_levels, red_levels, bk, rk, bt, rt, bi, ri, bm, rm):
    levels_dict = {
        1: 0,
        2: 280,
        3: 660,
        4: 1140,
        5: 1720,
        6: 2400,
        7: 3180,
        8: 4060,
        9: 5040,
        10: 6120,
        11: 7300,
        12: 8580,
        13: 9960,
        14: 11440,
        15: 13020,
        16: 14700,
        17: 16480,
        18: 18360
    }
    blue_exp = sum([levels_dict[i] for i in blue_levels])
    red_exp = sum([levels_dict[i] for i in red_levels])

    '''picked = []
    picked.append([idx_name_dict[champ] for champ in champions])
    picked = picked[0]'''

    b_picked, r_picked = [], []
    for i, champ in enumerate(champions):
        if i < 5:
            try:
                b_picked.append(idx_name_dict[champ])
            except:
                pass
        else:
            try:
                r_picked.append(idx_name_dict[champ])
            except:
                pass

    
    five_hot1 = np.zeros((len(champ_dict),), dtype=int)
    for j in b_picked:
        five_hot1[j] = 1
    five_hot2 = np.zeros((len(champ_dict),), dtype=int)
    for k in r_picked:
        five_hot2[k] = 1
    data = [timestamp] +  list(np.concatenate((five_hot1, five_hot2))) + [blue_gold/100000] + [red_gold/100000]
    data = data + [blue_exp/91800] + [red_exp/91800] + [bk/50] + [rk/50] + [bt/11] + [rt/11] + [bi/3]+ [ri/3] + bm + rm
    return data

def export_frame(matchId, frame):
    frame = np.array(frame)
    '''
    data architecture:
        time        (1)
        champions   (304 @ seraphine release)
        total gold  (2) 305
        total exp   (2)
        blue kills  (1)
        red kills   (1)
        blue towers (1)
        red towers  (1)
        blue inhibs (1)
        red inhibs  (1)
        blue monster(7) [air, earth, fire, water, elder, herald, baron]
        red monster (7)
    '''

    match = get_match(key, matchId).json()
    players = match['participants']
    
    champ_ids = [player['championId'] for player in players]
    champs = [name_rid_dict[str(i)] for i in champ_ids]

    bg = frame[305] * 100000
    rg = frame[306] * 100000

    bxp = frame[307]
    rxp = frame[308]

    bk = frame[309] * 50
    rk = frame[310] * 50

    bt = frame[311] * 11
    rt = frame[312] * 11

    bi = frame[313] * 3
    ri = frame[314] * 3

    bm = frame[315:322]
    # print(bm)
    rm = frame[322:]
    # print(rm)
    baron, elder = 2, 2

    if bm[6] == 1:
        baron = 0
    elif rm[6] == 1:
        baron = 1
    
    if bm[4] == 1:
        elder = 0
    elif rm[4] == 1:
        elder = 1

    # calculate exp, return average level
    bxp *= 91800/5
    rxp *= 91800/5
    
    b_lvl, r_lvl = None, None

    if bxp >= 18360: b_lvl = 18
    elif bxp >= 16480: b_lvl = 17
    elif bxp >= 14700: b_lvl = 16
    elif bxp >= 13020: b_lvl = 15
    elif bxp >= 11440: b_lvl = 14
    elif bxp >= 9960: b_lvl = 13
    elif bxp >= 8580: b_lvl = 12
    elif bxp >= 7300: b_lvl = 11
    elif bxp >= 6120: b_lvl = 10
    elif bxp >= 5040: b_lvl = 9
    elif bxp >= 4060: b_lvl = 8
    elif bxp >= 3180: b_lvl = 7
    elif bxp >= 2400: b_lvl = 6
    elif bxp >= 1720: b_lvl = 5
    elif bxp >= 1140: b_lvl = 4
    elif bxp >= 660: b_lvl = 3
    elif bxp >= 280: b_lvl = 2
    else: b_lvl = 1

    if rxp >= 18360: r_lvl = 18
    elif rxp >= 16480: r_lvl = 17
    elif rxp >= 14700: r_lvl = 16
    elif rxp >= 13020: r_lvl = 15
    elif rxp >= 11440: r_lvl = 14
    elif rxp >= 9960: r_lvl = 13
    elif rxp >= 8580: r_lvl = 12
    elif rxp >= 7300: r_lvl = 11
    elif rxp >= 6120: r_lvl = 10
    elif rxp >= 5040: r_lvl = 9
    elif rxp >= 4060: r_lvl = 8
    elif rxp >= 3180: r_lvl = 7
    elif rxp >= 2400: r_lvl = 6
    elif rxp >= 1720: r_lvl = 5
    elif rxp >= 1140: r_lvl = 4
    elif rxp >= 660: r_lvl = 3
    elif rxp >= 280: r_lvl = 2
    else: r_lvl = 1

    data = {
        'b1': champs[0],
        'b2': champs[1],
        'b3': champs[2],
        'b4': champs[3],
        'b5': champs[4],
        'r1': champs[5],
        'r2': champs[6],
        'r3': champs[7],
        'r4': champs[8],
        'r5': champs[9],
        'b1l': b_lvl,
        'b2l': b_lvl,
        'b3l': b_lvl,
        'b4l': b_lvl,
        'b5l': b_lvl,
        'r1l': r_lvl,
        'r2l': r_lvl,
        'r3l': r_lvl,
        'r4l': r_lvl,
        'r5l': r_lvl,
        'b_gold': int(round(bg)),
        'r_gold': int(round(rg)),
        'b_kills': int(round(bk)),
        'r_kills': int(round(rk)),
        'b_towers': int(round(bt)),
        'r_towers': int(round(rt)),
        'b_inhibs': int(round(bi)),
        'r_inhibs': int(round(ri)),
        'baron': str(baron),
        'elder': str(elder),
        'b_air': str(int(bm[0])),
        'b_earth': str(int(bm[1])),
        'b_fire': str(int(bm[2])),
        'b_water': str(int(bm[3])),
        'b_herald': str(int(bm[5])),
        'r_air': str(int(rm[0])),
        'r_earth': str(int(rm[1])),
        'r_fire': str(int(rm[2])),
        'r_water': str(int(rm[3])),
        'r_herald': str(int(rm[5]))
    }
    # print(data['r_water'])

    return data