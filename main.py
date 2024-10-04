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
    msgSent = 0
    previousGameId = 0
    # previousMsgOverwritten = 0
    # previousMsg = ''
    while 1 == 1:
        baseUrl = 'https://api.wc3stats.com'
        endpoint = '/gamelist'
        url = baseUrl + endpoint
        r = re.get(url = url)
        r = r.json()
        body = r['body']
        #go through the list of games and add the gameids to a list if the game[map] contains the string bfme
        bodyLen = len(body)
        gamesChecked = 0
        bfmeGameCounter = 0
        print(bodyLen)
        for game in body:
            gamesChecked = gamesChecked + 1
            if 'bfme' in game['map'].lower():
                bfmeGameCounter = 1
                print(listOfGameIds)
                print(game['id'])
                print(f'Previous: {previousGameId}, Current: {game['id'] }')
                if previousGameId != game['id'] and message is not None:
                    await message.edit(content=f"{previousMsg}  - Game Started/Removed")
                    message = None
                    msgSent = 0
                    print('message set to None')

                if game['id'] not in listOfGameIds:# and message == None:
                    currentGameId = game['id']
                    previousGameId = currentGameId
                    listOfGameIds.append(game['id'])
                    if message is None:
                        print('I send message.')
                        message = await send_message(channelId, f"Gamename: {game['name']} - Server: {game['server']} - Slots: {game['slotsTaken']}/{game['slotsTotal']}")
                elif game['id'] in listOfGameIds and message is not None and msgSent == 0:
                    print('I edit message.')
                    await message.edit(content=f"Gamename: {game['name']} - Server: {game['server']} - Slots: {game['slotsTaken']}/{game['slotsTotal']}")
                    previousMsg = f"Gamename: {game['name']} - Server: {game['server']} - Slots: {game['slotsTaken']}/{game['slotsTotal']}"
            if gamesChecked == bodyLen and bfmeGameCounter == 0 and message is not None:
                await message.edit(content=f"{previousMsg}  - Game Started/Removed")
                message = None
                msgSent = 0
                print('message set to None')
        await run_blockerFunc(blockerFunc, 45) 
        



client.run(discordAPIKey)