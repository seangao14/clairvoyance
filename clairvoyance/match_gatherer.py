import requests
import json
import numpy as np
import pandas as pd
import time
import pickle

from tqdm import tqdm
from riot_api_helpers import *
from config import key

challengers = get_challengers(key).json()
challenger_names = [i['summonerName'] for i in challengers['entries']]

accountIds = []
for name in tqdm(challenger_names):
    try:
        time.sleep(1.21)
        id = get_summoner(key, name).json()['accountId']
        accountIds.append(id)
    except:
        time.sleep(10)

pickle.dump(accountIds, open('data/accountIds.p', 'wb'))


gameIds = []
for idx in tqdm(accountIds):
    try:
        time.sleep(1.21)
        matches = get_matchlist(key, idx).json()
        for match in matches['matches']:
            if match['queue'] == 420 and match['gameId'] not in gameIds:
                gameIds.append(match['gameId'])
    except:
        time.sleep(10)

pickle.dump(gameIds, open('data/gameIds.p', 'wb'))