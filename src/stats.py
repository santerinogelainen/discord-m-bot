import json
import requests
from config import Config

class Stats:

    username = None
    urls = {"ow": "https://owapi.net/api/v3/u/{un}/blob", "osu": "https://osu.ppy.sh/api/get_user?k=" + Config.token["osu"] + "&u={un}"}

    def __init__(self, username):
        self.username = username

    def get(self, apitype):
        if apitype in self.urls:
            if ("#" in self.username and apitype == "ow"):
                self.username = self.username.replace("#", "-")

            url = self.urls[apitype].replace("{un}", self.username)
            j = self.request(url)
            if ("error" in j or j == []):
                return "Username not found."
            else:
                message = self.parse(apitype, j)
                return message
        else:
            return "Unknown type: " + apitype

    def request(self, url):
        headers = {
            'User-Agent': 'Python Discord M-Bot'
        }
        try:
            r = requests.get(url, headers=headers)
            data = json.loads(r.text)
        except:
            return False
        return data

    def parse(self, apitype, data):
        message = "**" + self.username + "**\n\n"
        if apitype == "ow":
            if (data["us"] is not None):
                message += self.generateOWMessage("US", data["us"])
            if (data["eu"] is not None):
                message += self.generateOWMessage("EU", data["eu"])
            if (data["kr"] is not None):
                message += self.generateOWMessage("KR", data["kr"])
        elif apitype == "osu":
            rank = str(data[0]["pp_rank"])
            crank = str(data[0]["pp_country_rank"]) + " " + data[0]["country"]
            pp = str(int(float(data[0]["pp_raw"]))) + "pp"
            acc = str(round(float(data[0]["accuracy"]), 2)) + "%"
            message += "__GLOBAL__: #" + rank + "\n__COUNTRY__: #" + crank + "\n__PP__: " + pp + "\n__ACCURACY__: " + acc
        return message

    def generateOWMessage(self, name, region):
        rank = region["stats"]["competitive"]["overall_stats"]["comprank"]
        heroes = region["heroes"]["playtime"]["competitive"]
        hero = max(heroes.keys(), key=(lambda k: heroes[k]))
        message = "__" + name + "__: " + str(rank) + "sr\nMost played hero: " + hero + "\n\n"
        return message
