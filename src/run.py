import discord
import asyncio
import os
import player

client = discord.Client()
music = player.Player(client)

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("-----")

@client.event
async def on_message(message):


    #!join
    if (message.content.startswith('!join') and message.author != client.user):
        if (client.is_voice_connected(message.server)):
            await client.send_message(message.channel, "Error, already in a channel. Type !leave to leave the channel.")
            return

        channelstr = message.content.split()[-1];
        if (channelstr == "!join"):
            await client.send_message(message.channel, "Error, channel not specified.")
            return
        else:
            channels = client.get_all_channels()
            for curchannel in channels:
                if (curchannel.name == channelstr and curchannel.type == discord.ChannelType.voice):
                    channel = curchannel
                    break

        try:
            channel
        except NameError:
            await client.send_message(message.channel, "Error, channel not found.")
            return
        else:
            voice = await client.join_voice_channel(channel)
            music.set_channel(voice, message.channel)

    #!leave
    if (message.content.startswith('!leave') and message.author != client.user):
        if (client.is_voice_connected(message.server)):
            await client.voice_client_in(message.server).disconnect()
        else:
            await client.send_message(message.channel, "Error, bot is not in a voice channel.")

    #!play
    if (message.content.startswith('!play') and message.author != client.user):
        url = message.content.split()[-1]
        started = await music.play_song(url)
        if not started:
            await client.send_message(message.channel, "Error, bot not in a voice channel. Type !join <channel name> to join a voice channel.")

    #!queue
    if ((message.content.startswith('!queue') or message.content.startswith('!q')) and message.author != client.user):
        url = message.content.split()[-1]
        if (url == "!queue" or url == "!q"):
            await client.send_message(message.channel, str(len(music.queue)) + " songs in queue.")
            return
        else:
            added = music.add_to_queue(url)
            if added:
                await client.send_message(message.channel, "Song(s) added to the queue. " + str(len(music.queue)) + " song(s) in queue.")
            else:
                await client.send_message(message.channel, "Not a youtube link or the video/playlist is not available.")

    #!pause
    if (message.content.startswith('!pause') and message.author != client.user):
        music.pause_song()

    #!skip
    if (message.content.startswith('!skip') and message.author != client.user):
        music.next_song()


    #!clear
    if (message.content.startswith('!clear') and message.author != client.user):
        param = message.content.split()[-1];
        if param == "queue" or param == "q":
            music.clear_queue()
            await client.send_message(message.channel, "Queue cleared.")

    #!shutdown
    if ((message.content.startswith('!shutdown') or message.content.startswith('!kys')) and message.author != client.user and message.author == message.server.owner):
        if (client.is_voice_connected(message.server)):
            await client.voice_client_in(message.server).disconnect()

        await client.send_message(message.channel, "Shutting down bot...")
        await client.logout()

    #!restart
    if (message.content.startswith('!restart') and message.author != client.user and message.author == message.server.owner):
        if (client.is_voice_connected(message.server)):
            await client.voice_client_in(message.server).disconnect()

        await client.send_message(message.channel, "Restarting bot...")
        path = os.path.realpath(__file__)
        await client.logout()
        os.system(path)

client.run("your thing config file to do")
