import json
import requests
import pprint
import urllib.parse
from clairvoyance.config import key
import clairvoyance.riot_api_helpers as riot

class Point:
    def __init__(self, timestamp, win_percent):
        self.timestamp = timestamp
        self.win_percent = win_percent

class Frame:
    def __init__(self, idx, timestamp, events):
        self.idx = idx
        self.timestamp = timestamp
        self.events = events

class Event:
    def __init__(self, name, team):
        self.team = team
        self.name = name

def get_frames(game_id):
    # get timeline
    res = riot.get_timeline(key, game_id)
    if res.status_code == 404:
        print("Error: match id " + game_id + " does not exist.")
        return -1
    timeline_data = res.json()
    frame_data = timeline_data["frames"]
    frames = []
    idx = 0
    for f in frame_data:
        events = []
        for e in f["events"]:
            if e["type"] == 'ELITE_MONSTER_KILL':
                if e["monsterType"] == 'DRAGON': 
                    new_event = Event(e["monsterSubType"]+"_KILL", 0 if e["killerId"] < 5 else 1) 
                else:
                    new_event = Event(e["monsterType"]+"_KILL", 0 if e["killerId"] < 5 else 1)
                events.append(new_event)
            elif e["type"] == 'BUILDING_KILL':
                new_event = Event(e["buildingType"]+"_KILL", 0 if e["teamId"] == 200 else 1)
                events.append(new_event)
            elif e["type"] == 'CHAMPION_KILL':
                new_event = Event(e["type"], 0 if e["victimId"] > 4 else 1)
                events.append(new_event)
        new_frame = Frame(idx, f["timestamp"], events)
        idx += 1
        frames.append(new_frame)
    return frames
    

