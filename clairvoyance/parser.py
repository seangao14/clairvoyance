import numpy as np
from champ_utils import idx_rid_dict as champ_dict

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
                if timeline['frames'][f_idx]['events'][e_idx]['teamId'] == 100: # 100 = blue team
                    bt -= 1
                else:
                    rt -= 1

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
        frame.extend(brmk[0])
        frame.extend(brmk[1])

        data.append(frame)
        y.append(winner)
    return data, y