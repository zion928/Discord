'''
KR Riot API End Point

-> 	kr.api.riotgames.com

quote() : url to encode
'''

# encid : 5ClrZV6I5PMUl6byGJ7MVejLfW2YfGxylkY999B6q1zbf4w
# puuid : Fy50ddrXuPpwZMInrRrZPsT2tCAHlQFrI5G9NI_-Lu9R91L4i7S09sbB0tquRcr-ST3u3NJdEJCi9A

import requests
import json
from urllib.parse import quote
from typing import MutableSequence, Any
from reProcessChampion import reProcessChampionLists
from collections import Counter

with open('championInfo.json') as f:
    champInfo = json.load(f)

mapRankName = {
    'RANKED_FLEX_SR' : "Flex 5:5 Rank",
    'RANKED_SOLO_5x5' : "Personal/Duo Rank"
}

class riotAPIRequest(object):
    def __init__(self, riotapikey) -> None:
        self.KRRegionAPIEndPoint='https://kr.api.riotgames.com'
        self.AsiaRegionAPIEndPoint='https://asia.api.riotgames.com'
        self.puuidEnd = "/lol/summoner/v4/summoners/by-name/"# /lol/summoner/v4/summoners/by-name/{summonerName}
        self.personalInfoEnd = "/lol/league/v4/entries/by-summoner/"  #/lol/league/v4/entries/by-summoner/{encryptedSummonerId}
        self.personalChampionMastery = "/lol/champion-mastery/v4/champion-masteries/by-summoner/"#/lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}
        self.match = "/lol/match/v5/matches/by-puuid/" #/lol/match/v5/matches/by-puuid/{puuid}/ids
        self.matchlist = "/lol/match/v5/matches/" #/lol/match/v5/matches/{matchId}
        self.req_header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.96 Safari/537.36",
            "Accept-Language": "ko-KR",
            "X-Riot-Token": riotapikey
        }
    
    def reOpenJSON(self):
        with open('championInfo.json') as f:
            champInfo = json.load(f)
    
    def update_CInfo(self):
        if requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0] != champInfo["Version"]:
            reProcessChampionLists()
            self.reOpenJSON()
        else:
            pass
    
    def get_puuid_and_encryptedID(self,name) -> bool:
        getResponseJSON = requests.get(self.KRRegionAPIEndPoint + self.puuidEnd + quote(name),headers=self.req_header).json()
        summonerKeyBox = {
            'encid' : getResponseJSON['id'],
            'puuid' : getResponseJSON['puuid']
        }
        return summonerKeyBox
        
    def getPersonalChampionMastery(self,name) -> bool:
        self.update_CInfo()
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            mastery = requests.get(self.KRRegionAPIEndPoint + self.personalChampionMastery + keybox['encid'], headers=self.req_header).json()[0]
            chid = mastery['championId']
            chlv = mastery['championLevel']
            chpoint = mastery['championPoints']
            reProcessMastery = {
                'championname' : champInfo[str(chid)]["name"],
                'championlevel' : chlv,
                'championpoint' : chpoint,
                'championImage' : champInfo[str(chid)]["image"]    
            }
            return reProcessMastery
        except KeyError as e: #For not-Existing ID
            return  False
    
    def getPersonalChampionMasteries(self,name) -> bool:
        self.update_CInfo()
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            mastery = requests.get(self.KRRegionAPIEndPoint + self.personalChampionMastery + keybox['encid'], headers=self.req_header).json()
            reprocessmastery = dict()
            if len(mastery) > 3:
                mastery = mastery[0:3]
                for i in mastery:
                    chid = i['championId']
                    chlv = i['championLevel']
                    chpoint = i['championPoints']
                    reprocessmastery[champInfo[str(chid)]["name"]] = {
                        'championlevel' : chlv,
                        'championpoint' : chpoint,
                        'championImage' : champInfo[str(chid)]["image"]
                    }
            else:
                for i in mastery:
                    chid = i['championId']
                    chlv = i['championLevel']
                    chpoint = i['championPoints']
                    reprocessmastery[champInfo[str(chid)]["name"]] = {
                        'championlevel' : chlv,
                        'championpoint' : chpoint,
                        'championImage' : champInfo[str(chid)]["image"]
                    }
            return reprocessmastery
        except KeyError as e: #For not-Existing ID
            return  False
        
    def getPersonalGameRecord(self,name) -> bool:
        self.update_CInfo()
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            getMastery = self.getPersonalChampionMastery(name)
            getResponseJSON = requests.get(self.KRRegionAPIEndPoint + self.personalInfoEnd + keybox['encid'], headers=self.req_header).json()
            reProcessRecord = dict()
            for i in getResponseJSON:
                reProcessRecord[mapRankName[i['queueType']]] = {
                    'tier' : f"{i['tier']}",
                    'rank' : f"{i['rank']}",
                    'leaguepoint' : i['leaguePoints'],
                    'win' : i['wins'],
                    'loss' : i['losses']
                }
            summary = {
                "Record" : reProcessRecord,
                "ChampionMastery" : getMastery
            }
            return summary
        except KeyError as e: #For not-Existing ID
            return  False
        
    def get_recent_match_ids(self, name) -> bool:
        default = "start=0"
        GameType = "type=ranked"
        GameCount = "count=30"
        Game = "?"+GameType+"&"+default+"&"+GameCount
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            matchlist = requests.get(self.AsiaRegionAPIEndPoint+self.match+keybox['puuid']+"/ids"+Game, headers=self.req_header).json()
        
            return matchlist
        except KeyError as e: #For not-Existing ID
            return  False
        
    def get_positon(self, name, matchid) -> bool:
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            matchData = requests.get(self.AsiaRegionAPIEndPoint+matchid, headers=self.req_header).json()
            
            position = matchData["info"]["participants"][]
            data = response.json()

            # Find the participant ID for the given summoner ID
            participant_id = next((identity["participantId"] for identity in data["participantIdentities"] 
                                if identity["player"]["summonerId"] == summoner_id), None)
        
            if not participant_id:
                return None
        
            # Get the team position for the participant ID
            team_position = next((participant["teamPosition"] for participant in data["participants"] 
                                if participant["participantId"] == participant_id), None)
        
            return team_position
        pass

    def analyze_main_and_sub_positions(self, summoner_id):
        solo_rank_ids, flex_rank_ids = self.get_recent_match_ids(summoner_id)
        all_match_ids = solo_rank_ids + flex_rank_ids

        # Fetch team positions for all matches
        positions = [self.get_team_position_for_match(match_id, summoner_id) for match_id in all_match_ids]

        # Count occurrences of each position
        position_counts = Counter(positions)

        # Sort by occurrence
        sorted_positions = sorted(position_counts.items(), key=lambda x: x[1], reverse=True)

        # Main position is the most frequent one
        main_position = sorted_positions[0][0]

        # Sub positions are the next most frequent ones
        sub_positions = [pos[0] for pos in sorted_positions[1:3]]

        return main_position, sub_positions