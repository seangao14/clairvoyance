import json
import requests
import urllib.parse
from clairvoyance.champ_utils import name_rid_dict as champ_dict
from clairvoyance.config import key
import clairvoyance.riot_api_helpers as riot

class Summoner:
    def __init__(self, id, name, icon, level, matches):
        self.id = id
        self.name = name
        self.icon = icon
        self.level = level
        self.matches = matches

def get_account_data(name):
    """Takes summoner name and returns a Summoner object if successful, or -1 if summoner not found/has no matches"""
    # get summoner
    r_1 = riot.get_summoner(key, name)
    if r_1.status_code == 404:
        print(f"Error: user {name} does not exist.")
        return -1
    if r_1.status_code >= 400:
        print(r_1.reason)
    account_data = r_1.json()
    account_id = account_data["accountId"]

    # get matches
    r_2 = riot.get_matchlist(key, account_id)
    if r_2.status_code == 404:
        print(f"Error: user {name} does not have any matches.")
        return -1
    match_data = r_2.json()

    matches = []
    gameIds = [i['gameId'] for i in match_data['matches']]
    
    '''
    id = None           # int
    champion = None     # str
    win = None          # bool
    kda = None          # [k, d, a]
    ss = None           # summoners spell, [ss1, ss2]
    length = None       # int, in seconds
    queue = None        # str
    '''

    for game in gameIds:
        match = riot.get_match(key, game).json()
        # identify the user
        id_ = None
        for m in match['participantIdentities']:
            player = m['player']
            if player['summonerName'].lower() == name.lower():
                id_ = m['participantId']
                break
        gamer = match['participants'][id_-1]
        stats = gamer['stats']
        
        champ_id = gamer['championId']
        champion = champ_dict[f'{champ_id}']

        win = stats['win']

        kda = [stats['kills'], stats['deaths'], stats['assists']]

        ss = [gamer['spell1Id'], gamer['spell2Id']]

        match_len = match['gameDuration']

        queue_id = match['queueId']
        if queue_id == 400:
            queue_type = 'Normal Draft'
        elif queue_id == 420:
            queue_type = 'Ranked Solo/Duo'
        elif queue_id == 430:
            queue_type = 'Normal Blind'
        else:
            queue_type = 'Ranked Flex'

        match_dict = {
            'id': game,
            'champion': champion,
            'win': win,
            'kda': kda,
            'ss': ss,
            'length': match_len,
            'queue': queue_type
        }
        matches.append(match_dict)



    summoner = Summoner(account_id, account_data["name"], account_data["profileIconId"], account_data["summonerLevel"], matches)
    return summoner
    