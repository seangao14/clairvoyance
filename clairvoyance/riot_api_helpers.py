import json
import requests
import urllib.parse

'''def url_to_json(url):
    return requests.get(url).json()'''

def get_summoner(api_key, arg, region='na1'):
    '''
    @arg summoners name
    returns a json
    '''
    url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{urllib.parse.quote(arg)}?api_key={api_key}'
    return requests.get(url)

def get_matchlist(api_key, arg, region='na1'):
    '''
    @arg takes accountId
    returns a json
    '''
    url = f'https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{urllib.parse.quote(arg)}?queue=400&queue=420&queue=430&queue=440&endIndex=10&api_key={api_key}'
    return requests.get(url)

def get_match(api_key, arg, region='na1'):
    '''
    @arg takes gameId
    returns a json
    '''
    url = f'https://{region}.api.riotgames.com/lol/match/v4/matches/{arg}?api_key={api_key}'
    return requests.get(url)

def get_timeline(api_key, arg, region='na1'):
    '''
    @arg takes matchId
    returns big json :)
    '''
    url = f'https://{region}.api.riotgames.com/lol/match/v4/timelines/by-match/{arg}?api_key={api_key}'
    return requests.get(url)

def get_challengers(api_key, region='na1'):
    url = f'https://{region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    return requests.get(url)