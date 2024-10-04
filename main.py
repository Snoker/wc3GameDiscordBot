import json, discord
import pandas as pd
import typing
import requests as re
import datetime as dt
import time 



with open('configSecret.json') as f:
    secretsData = json.load(f)
discordAPIKey = secretsData['discordAPIKey']

with open('config.json') as f:
    configData = json.load(f)
channelId = configData['channelId']

client = discord.Client(intents=discord.Intents.default())
guild = discord.Guild

listOfGameIds = []

def blockerFunc(secondsToBlock):
    time.sleep(secondsToBlock)
    return True

async def run_blockerFunc(blockerFunc: typing.Callable, secondsToBlock: int):
    return await client.loop.run_in_executor(None, blockerFunc, secondsToBlock)

async def send_message(channel_id, message):
    channel = client.get_channel(channel_id)
    return await channel.send(message)



@client.event
async def on_ready():
    message = None
    while 1 == 1:
        baseUrl = 'https://api.wc3stats.com'
        endpoint = '/gamelist'
        url = baseUrl + endpoint
        r = re.get(url = url)
        r = r.json()
        body = r['body']
        #go through the list of games and add the gameids to a list if the game[map] contains the string bfme
        for game in body:
            if 'bfme' in game['map'].lower():
                print(message)
                print(listOfGameIds)
                print(game['id'])
                if game['id'] not in listOfGameIds:# and message == None:
                    listOfGameIds.append(game['id'])
                    if message is None:
                        message = await send_message(channelId, f"Gamename: {game['name']} - Server: {game['server']} - Slots: {game['slotsTaken']}/{game['slotsTotal']}")
                elif game['id'] in listOfGameIds and message is not None:
                    await message.edit(content=f"Gamename: {game['name']} - Server: {game['server']} - Slots: {game['slotsTaken']}/{game['slotsTotal']}")
                elif message is not None:
                    await message.edit(content=f"{message} (STARTED/REMOVED)")
                    message = None
                print(f"Gamename: {game['name']} - Server: {game['server']} - Slots: {game['slotsTaken']}/{game['slotsTotal']}")
        await run_blockerFunc(blockerFunc, 30) 
        



client.run(discordAPIKey)