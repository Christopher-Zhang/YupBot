import os
import requests
import json
import time
import datetime
from datetime import timedelta

class PandaAPI:
    def __init__(self):
        self.base_url = 'https://api.pandascore.co'
        self.token = os.getenv('PANDA_TOKEN')
        self.auth = '?token=' + self.token
        self.LCS_ID = 4198
        self.ONE_WEEK = timedelta(days=7)
        self.GMT_TO_EST = timedelta(hours=5)
        time_offset = -time.timezone
        is_dst = time.daylight and time.localtime().tm_isdst > 0
        self.LOCAL_OFFSET = round(time_offset / (60 * 60)) + is_dst

    def query_panda(self, path, parameters):
        response = requests.get(self.base_url + path + self.auth + parameters)
        return json.loads(response.text)
    def get_champs(self):
        # response = requests.get("https://api.pandascore.co/lol/champions?token=" + os.getenv('PANDA'))
        # json_data = json.loads(response.text)
        # return json_data
        path = "/lol/champions"
        parameters = "&page[size]=1"
        return self.query_panda(path,parameters)

    # gets champion data by name 
    def get_champ(self, name):
        path = "/lol/champions"
        parameters = "&search[name]=" + name
        return self.query_panda(path,parameters)

    # gets champ icon url by name
    def get_champ_portrait(self, name):
        champ = self.get_champ(name)
        if len(champ) > 0:
            return champ[0]["image_url"]
        return None

    # gets a list of all the leagues from panda api
    def get_leagues(self):
        path = "/lol/leagues"
        parameters = ""
        return self.query_panda(path,parameters)
    def get_matches(self, league_id_string):
        parameters = "&filter[league_id]=" + league_id_string
        path = "/lol/matches"
        return self.query_panda(path,parameters)
    # gets 
    def get_upcoming_matches(self, league_id_string):
        parameters = "&filter[league_id]="+league_id_string+"&sort=begin_at"
        path = "/lol/matches/upcoming"
        return self.query_panda(path,parameters)
    # returns array of match objects within the next week
    def get_matches_within_week(self, league_id_string):
        now = datetime.datetime.now()
        week_from_now = now + self.ONE_WEEK
        matches = self.get_upcoming_matches(league_id_string)
        for match in reversed(matches):
            match_time = match["begin_at"]
            match_time = datetime.datetime.strptime(match_time, "%Y-%m-%dT%H:%M:%SZ")
            if match_time < week_from_now:
                break
            matches.pop()
        return matches
    def match_to_schedule_string(self, match, utc_offset):
        utc_offset = timedelta(hours=utc_offset)
        team1 = match["opponents"][0]["opponent"]["acronym"]
        team2 = match["opponents"][1]["opponent"]["acronym"]
        matchup = team1 + " vs " + team2
        match_time = match["begin_at"]
        match_time = datetime.datetime.strptime(match_time, "%Y-%m-%dT%H:%M:%SZ") - utc_offset
        date_string = match_time.strftime("%x")
        time_string = match_time.strftime("%I:%M%p")
        if time_string[0] == '0':
            time_string = time_string[1:]
        day_of_week = match_time.strftime("%A")
        day = match_time.strftime('%d')
        if day[0] == '0':
            day = day[1]
        month = match_time.strftime('%m')
        if month[0] == '0':
            month = month[1]
        full_string = matchup + " at " + time_string + " on " + day_of_week + " " + month + "/" + day
        return full_string
    def generate_schedule_message(self, matches, utc_offset):
        message = ""
        for match in matches:
            message += self.match_to_schedule_string(match,-self.LOCAL_OFFSET) + "\n"
        return message
    def get_schedule_message(self, league_id_string):
        matches = self.get_matches_within_week(league_id_string)
        message = self.generate_schedule_message(matches,-self.LOCAL_OFFSET)
        return message