import requests
import json
import numpy as np
import pandas as pd
import time
import pickle

from tqdm import tqdm
from riot_api_helpers import *
from game_parser import *
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

X, y = [], []

for ids in tqdm(gameIds):
    try:
        match = get_match(key, f'{ids}').json()
        timeline = get_timeline(key, f'{ids}').json()
        game, win = parse_game(timeline, match)
        X = X + game
        y = y + win
        time.sleep(0.5)
    except Exception as e:
        print(f'error: {e}')
        time.sleep(2)

X = np.array(X)
y = np.array(y)

with open('data/training/X.npy', 'wb') as f:
    np.save(f, X)
with open('data/training/y.npy', 'wb') as f:
    np.save(f, y)