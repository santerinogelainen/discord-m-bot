import discord
import asyncio
import json
import requests
from urllib.parse import urlparse
from config import Config

class Player:

    #variables
    queue = []
    client = None
    player = None #ytdl player object
    voicechannel = None
    textchannel = None

    def __init__(self, client):
        self.client = client

    #send a message to a text channel, used in synchronous methods, since create_ytdl_player only accepts synchronous callable methods in after parameter
    def send_coroutine_message(self, text):
        msg = self.client.send_message(self.textchannel, text)
        cor = asyncio.run_coroutine_threadsafe(msg, self.client.loop)
        try:
            cor.result()
        except:
            pass

    #set voice and text channels
    def set_channel(self, voicechannel, textchannel):
        self.voicechannel = voicechannel
        self.textchannel = textchannel

    async def play_queue(self):
        if not self.check_queue():
            await self.client.send_message(self.textchannel, "No songs in queue. Add song(s) by typing !q <link>")
            return False
        else:
            try:
                self.player = await self.voicechannel.create_ytdl_player(self.queue[0], after=self.next_song_threadsafe)
                self.start_song()
            except:
                await self.client.send_message(self.textchannel, "Invalid link. Skipping song...")
                self.queue.pop(0)
                await self.play_queue()
                return

            self.queue.pop(0)
            await self.client.send_message(self.textchannel, "Now playing: " + self.player.title)

    #play a song
    async def play_song(self, url):
        if self.voicechannel is None:
            return False
        else:
            self.pause_song()
            if self.player is not None:
                self.resume_song()
            else:
                if url == "!play":
                    await self.play_queue()
                    return True
                else:
                    try:
                        self.player = await self.voicechannel.create_ytdl_player(url, after=self.next_song_threadsafe)
                        self.start_song()
                    except:
                        await self.client.send_message(self.textchannel, "Invalid link.")
                        return
                    await self.client.send_message(self.textchannel, "Now playing: " + self.player.title)
        return True

    #check if there are songs in the queue
    def check_queue(self):
        if self.queue == []:
            self.player = None
            return False
        else:
            return True

    #synchronous change to next song, used in create_ytdl_player after parameter
    def next_song_threadsafe(self):
        if not self.check_queue():
            self.send_coroutine_message("No more songs in queue. Add song(s) by typing !q <link>")
            return False
        else:
            self.stop_song()
            tempplayer = self.voicechannel.create_ytdl_player(self.queue[0], after=self.next_song_threadsafe)
            cor = asyncio.run_coroutine_threadsafe(tempplayer, self.client.loop)
            self.queue.pop(0)
            try:
                self.player = cor.result()
            except:
                self.send_coroutine_message("Invalid link. Skipping song...")
                self.next_song_threadsafe()
                return

            self.start_song()
            self.send_coroutine_message("Now playing: " + self.player.title)
            return True

    def next_song(self):
        self.stop_song()


    #add a song to queue
    def add_to_queue(self, url):
        parsed = urlparse(url)
        print(parsed)
        if (parsed.scheme != '' and (parsed.netloc == "youtube.com" or parsed.netloc == "www.youtube.com" or parsed.netloc == "youtu.be") and parsed.query != ''):
            isplaylist = self.is_playlist(parsed)
            if isplaylist:
                if parsed.path == "/playlist":
                    urls = self.get_playlist_urls(parsed)
                    if urls != False:
                        for cururl in urls:
                            self.queue.append(cururl)
                    else:
                        return False
                else:
                    url = parsed.scheme + "://" + parsed.netloc + parsed.path + "?" + parsed.query.split("&")[0]
                    self.queue.append(url)
            else:
                self.queue.append(url)
            return True
        else:
            return False

    def is_playlist(self, parsedurl):
        if (parsedurl.path == "/playlist" or parsedurl.query.find("&list")):
            return True
        else:
            return False

    def get_playlist_urls(self, parsedurl):
        urls = []
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=" + parsedurl.query.split("&")[0].split("=")[1] + "&key=" + Config.token["youtube"] + "&maxResults=50")
            data = json.loads(r.text)
            for item in data["items"]:
                urls.append("https://www.youtube.com/watch?v=" + item["snippet"]["resourceId"]["videoId"])
        except:
            return False
        while "nextPageToken" in data:
            r = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=" + parsedurl.query.split("&")[0].split("=")[1] + "&key=" + Config.token["youtube"] + "&maxResults=50&pageToken=" + data["nextPageToken"])
            data = json.loads(r.text)
            for item in data["items"]:
                urls.append("https://www.youtube.com/watch?v=" + item["snippet"]["resourceId"]["videoId"])
        return urls

    #clear queue
    def clear_queue(self):
        self.queue = []

    #stop song
    def stop_song(self):
        if self.player is not None and self.player.is_playing():
            print("stopped song")
            self.player.stop()

    #start song
    def start_song(self):
        if self.player is not None:
            print("started song, volume: 0.5")
            self.player.volume = 0.5
            self.player.start()

    #resume song
    def resume_song(self):
        if self.player is not None and not self.player.is_playing():
            print("resuming song")
            self.player.resume()

    #pause song
    def pause_song(self):
        if self.player is not None and self.player.is_playing():
            print("paused song")
            self.player.pause()
