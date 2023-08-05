#!/usr/bin/env python3

from requests import Session
import json
from clint.textui import progress
from danmaku2ass import Danmaku2ASS
import os
import sys


def dd2ac_unit(dd):
    ac_tuple_c = (dd["Time"], dd["Color"], dd["Mode"], 25, 'unknown',
                  dd["Timestamp"], 'unknown')
    return {'c': ','.join(list(map(str, ac_tuple_c))),
            'm': dd['Message']}


def download(url, session, o):
    r = session.get(url, stream=True)
    with open(o, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024),
                                  expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()
    return o


def read_json(f):
    with open(f, 'r') as fi:
        d = json.load(fi)
    return d


def dd2ac(f):
    ac_list = []
    with open(f, 'r') as fi:
        d = json.load(fi)
    for comment in d['Comments']:
        ac_list.append(dd2ac_unit(comment))
    return [[], [], ac_list]


def ass_from_dd(id, session, name=None):
    name = (name or str(id))
    f = name + ".json"
    download("http://acplay.net/api/v1/comment/" + str(id), session, f)
    ac_list = dd2ac(f)
    with open(f, 'w') as fi:
        json.dump(ac_list, fi)
    Danmaku2ASS(f, name+".ass", 1440, 800, duration_marquee=10)
    os.remove(f)

# 
# 
# headers = {"Accept": "application/xml"}

def main():
    session = Session()
    response = session.get("http://acplay.net/api/v1/searchall/" + sys.argv[1])
    search_result = json.loads(response.content.decode('utf8'))["Animes"]
    for index, bangumi in enumerate(search_result):
        print(index, bangumi['Title'])
    bangumi_selected = int(input("Select Bangumi: "))
    episodes = search_result[bangumi_selected]['Episodes']
    for index, episode in enumerate(episodes):
        print(index, episode['Title'])
    episode_selected = int(input("Select Episode (-1 for all): "))

    episode_list = []
    if episode_selected == -1:
        for episode in episodes:
            episode_list.append(episode)
    else:
        episode_list.append(episodes[episode_selected])

    for episode in episode_list:
        ass_from_dd(episode['Id'], session, episode['Title'])
