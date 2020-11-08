import json
import requests
import urllib.parse
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
        print("Error: user " + name + " does not exist.")
        return -1
    account_data = r_1.json()
    account_id = account_data["accountId"]

    # get matches
    r_2 = riot.get_matchlist(key, account_id)
    if r_2.status_code == 404:
        print("Error: user " + name + " does not have any matches.")
        return -1
    match_data = r_2.json()
    matches = match_data["matches"]
    summoner = Summoner(account_id, account_data["name"], account_data["profileIconId"], account_data["summonerLevel"], matches)
    return summoner
    