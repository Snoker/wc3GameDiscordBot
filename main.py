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

def blockerFunc(secondsToBlock):
    time.sleep(secondsToBlock)
    return True

async def run_blockerFunc(blockerFunc: typing.Callable, secondsToBlock: int):
    return await client.loop.run_in_executor(None, blockerFunc, secondsToBlock)

async def send_message(channel_id, message):
    channel = client.get_channel(channel_id)
    return await channel.send(message)

def validate_game_data(game_data):
    required_keys = ['name', 'host', 'server', 'map', 'slotsTaken', 'slotsTotal']
    return all(key in game_data for key in required_keys)

def create_embed_fields(game_data):
    return [
        {"name": "Server", "value": game_data['server'], "inline": True},
        {"name": "Map", "value": game_data['map'], "inline": False},
        {"name": "Slots", "value": f"{game_data['slotsTaken']}/{game_data['slotsTotal']}", "inline": False}
    ]

def create_new_embed(game_data):
    if not validate_game_data(game_data):
        return None
    
    embed = discord.Embed(
            color=0x1abc9c,
            title=game_data['name'],
            url="https://wc3bfme.net/index.php?forums/frontpage/"
        )
        
    fields = create_embed_fields(game_data)
    for field in fields:
        embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])

    embed.set_footer(text="Powered by https://wc3stats.com")
    embed.set_author(name=game_data['host'])

    return embed




client = discord.Client(intents=discord.Intents.default())
guild = discord.Guild
listOfGameIds = []
gameMessageDict = {}


@client.event
async def on_ready():
    message = None
    while 1 == 1:
        baseUrl = 'https://api.wc3stats.com'
        endpoint = '/gamelist'
        url = baseUrl + endpoint
        r = re.get(url = url)
        r = r.json()
        # with open('testData.json') as f:
        #     testData = json.load(f)
        # r = testData
        body = r['body']
        allGameIds = [game['id'] for game in body]
        for game in body:
            if 'bfme' in game['map'].lower():
                gameId = game['id']
                if gameId not in listOfGameIds:
                    print('I send message.')
                    listOfGameIds.append(gameId)
                    msgEmbed = create_new_embed(game)
                    channel = client.get_channel(channelId)
                    message = await channel.send(embed=msgEmbed)
                    gameMessageDict[gameId] = {
                        "messageId": message.id,
                        "embed": msgEmbed
                    }
                elif gameId in gameMessageDict:
                    print('I edit message.')
                    messageId = gameMessageDict[game['id']]["messageId"]
                    channel = client.get_channel(channelId)
                    message = await channel.fetch_message(messageId)
                    msgEmbed = create_new_embed(game)
                    await message.edit(embed=msgEmbed)
                    gameMessageDict[gameId]["embed"] = msgEmbed
            missingGameIds = [game_id for game_id in gameMessageDict if game_id not in allGameIds]
            for missingGameId in missingGameIds:
                print('I remove message.')
                messageId = gameMessageDict[missingGameId]["messageId"]
                channel = client.get_channel(channelId)
                message = await channel.fetch_message(messageId)
                msgEmbed = gameMessageDict[missingGameId]["embed"]
                msgEmbed.color = 0x808080
                await message.edit(content="~~Game Started/Removed~~",embed=msgEmbed)
                gameMessageDict.pop(missingGameId)
        await run_blockerFunc(blockerFunc, 3) 

client.run(discordAPIKey)