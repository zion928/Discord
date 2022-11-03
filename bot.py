
import discord
from discord.ext import commands

import requests
from riotwatcher import LolWatcher, ApiError

import asyncio
import os
import json
import yaml
from apiRequest import riotAPIRequest
import re  # Regex for youtube link
import warnings

from to import *
from date import *
# from opgg import *

intents = discord.Intents.default()
warnings.filterwarnings(action='ignore')
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command = None)  # 명령어 시작은 !


with open('config.yml') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

####################################################
bottoken = keys['Keys']['discordAPIToken']
riotapiKey = keys['Keys']['riotAPIToken']
apiCall = riotAPIRequest(riotapiKey)
# for lolplayersearch
tierScore = {
    'DEFAULT': 0,
    'IRON': 1,
    'BRONZE': 2,
    'SILVER': 3,
    'GOLD': 4,
    'PLATINUM': 5,
    'DIAMOND': 6,
    'MASTER': 7,
    'GRANDMASTER': 8,
    'CHALLENGER': 9
}


def tierCompare(solorank, flexrank):
    #solorank is higher
    if tierScore[solorank] > tierScore[flexrank]:
        return 0
    #flexrank is higher
    elif tierScore[solorank] < tierScore[flexrank]:
        return 1
    # same
    else:
        return 2

####################################################


@bot.event  # Use these decorator to register an event.
async def on_ready():  # on_ready() event : when the bot has finised logging in and setting things up
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Type !help or !도움말 for help"))
    print("New log in as {0.user}".format(bot))


# @bot.event
# async def on_ready():
#     print('Logged in as')
#     print(bot.user.name)
#     print(bot.user.id)
#     print('-------')




@bot.command()
async def ping(ctx):  # !ping 입력시
    await ctx.send('pong')  # ctx = context 호출


@bot.command()
async def test(ctx, *, arg):  # arg = argument 매개변수
    await ctx.send(arg)

@bot.command(aliases =["help","도움말"])
async def bot_help(ctx):
    if ctx.author == bot.user:
        return

    embed = discord.Embed(
        title="**How to Use Commands**", 
        description="To use command !recode : **!recode (Summoner Nickname)** \n To use command !most : **!most (Summoner Nickname)**",
        color=0x5CD1E5
        # ** 굵게 ** ' 작은 글씨 '
    )
    # embed.add_field(
    #     name="필드의 이름",
    #     value="필드의 값"
    # )
    # inline
    # false 가로 붙이기

    embed.set_footer(
        text="LMB",
        icon_url='https://i.imgur.com/ltiu4g8.png'
    )
    # 꼬리말 / 보통 입력한 사용자의 닉네임, 프로필 사진 추가
    # 혹은 원하는 프로필 정보
    # text = f"{ctx.message.author.name}"
    # icon_url = ctx.message.author.avatar.url
    await ctx.send(embed=embed)
    
@bot.command(aliases = ['r'])
async def recode(ctx):
    if ctx.author == bot.user:
        return
    try:
        if len(ctx.message.content.split(" ")) == 1:
            embed = discord.Embed(
                title="Summoner name not entered!", 
                description="", 
                color=0x5CD1E5)
            embed.add_field(
                name="Summoner name not entered",
                value="To use command !recode : !recode (Summoner Nickname) \n To use command !most : !most (Summoner Nickname)", 
                inline=False)
            embed.set_footer(
                text='Data by Official Riot API : https://developer.riotgames.com/',
                icon_url='https://i.imgur.com/ltiu4g8.png')
            await ctx.send("Summoner name not entered!", embed=embed)
        else:
            playerNickname = ' '.join((ctx.message.content).split(' ')[1:])
            # Return false if summoner not exist
            getPersonalRecordBox = apiCall.getPersonalGameRecord(
                playerNickname)
            if not getPersonalRecordBox:
                embed = discord.Embed(
                    title="Non-existent summoner", description="", color=0x5CD1E5)
                embed.add_field(name="The summoner for this nickname does not exist.",
                                value="Please check the summoner's name.", inline=False)
                embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                    icon_url='https://i.imgur.com/ltiu4g8.png')
                await ctx.send("The summoner for this nickname does not exist.", embed=embed)
            else:
                record = getPersonalRecordBox["Record"]
                keys = record.keys()
                mastery = getPersonalRecordBox["ChampionMastery"]
                if len(record) == 2:
                    solowinRatio = int((record['Personal/Duo Rank']['win'] / (
                        record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank']['loss'])) * 100)
                    flexwinRatio = int((record['Flex 5:5 Rank']['win'] / (
                        record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
                    solotier = record['Personal/Duo Rank']['tier']
                    flextier = record['Flex 5:5 Rank']['tier']
                    tc = tierCompare(solotier, flextier)
                    thumbnail = "lorem ipsum"
                    # Compare tier
                    if tc == 0:
                        thumbnail = solotier
                    elif tc == 1:
                        thumbnail = flextier
                    else:
                        thumbnail = solotier
                    print("Summoner's tier is "+thumbnail)
                    print(f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{thumbnail}.png?raw=true")
                    embed = discord.Embed(
                        title="Summoner recode search", description="", color=0x5CD1E5)
                    embed.add_field(name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['rank']}",
                                    value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L / Win Rate {solowinRatio}%", inline=False)
                    embed.add_field(name=f"Flex 5:5 Rank : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['rank']}",
                                    value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L / Win Rate {flexwinRatio}%", inline=False)
                    embed.add_field(
                        name=f"Most Used Champion : {mastery['championname']}", value=f"Proficiency Level : {mastery['championlevel']}.Lv / Champion Point : {mastery['championpoint']}pt")
                    embed.set_thumbnail(
                        url=f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{thumbnail}.png?raw=true")
                    embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                        icon_url='https://i.imgur.com/ltiu4g8.png')
                    await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

                elif len(record) == 0:
                    embed = discord.Embed(
                        title="Summoner recode search", description="", color=0x5CD1E5)
                    embed.add_field(name="Ranked Solo : Unranked",
                                    value="Unranked", inline=False)
                    embed.add_field(
                        name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.set_thumbnail(
                        url="https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_DEFAULT.png?raw=true")
                    embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                        icon_url='https://i.imgur.com/ltiu4g8.png')
                    await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

                elif len(record) == 1 and "Personal/Duo Rank" not in keys:
                    flexwinRatio = int((record['Flex 5:5 Rank']['win'] / (
                        record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
                    embed = discord.Embed(
                        title="Summoner recode search", description="", color=0x5CD1E5)
                    embed.add_field(name="Ranked Solo : Unranked",
                                    value="Unranked", inline=False)
                    embed.add_field(name=f"Flex 5:5 Rank : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['rank']}",
                                    value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L / Win Rate {flexwinRatio}%", inline=False)
                    embed.add_field(
                        name=f"Most Used Champion : {mastery['championname']}", value=f"Proficiency Level : {mastery['championlevel']}.Lv / Champion Point : {mastery['championpoint']}pt")
                    embed.set_thumbnail(
                        url=f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{record['Flex 5:5 Rank']['tier']}.png?raw=true")
                    embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                        icon_url='https://i.imgur.com/ltiu4g8.png')
                    await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

                elif len(record) == 1 and "Flex 5:5 Rank" not in keys:
                    solowinRatio = int((record['Personal/Duo Rank']['win'] / (
                        record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank']['loss'])) * 100)
                    embed = discord.Embed(
                        title="Summoner recode search", description="", color=0x5CD1E5)
                    embed.add_field(name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['rank']}",
                                    value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L / Win Rate {solowinRatio}%", inline=False)
                    embed.add_field(
                        name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.add_field(
                        name=f"Most Used Champion : {mastery['championname']}", value=f"Proficiency Level : {mastery['championlevel']}.Lv / Champion Point : {mastery['championpoint']}pt")
                    embed.set_thumbnail(
                        url=f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{record['Personal/Duo Rank']['tier']}.png?raw=true")
                    embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                        icon_url='https://i.imgur.com/ltiu4g8.png')
                    await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)
    except BaseException as e:
        print(e)
        embed = discord.Embed(title="There was a bug in Logic.",
                                description="", color=0x5CD1E5)
        embed.add_field(name="There was a bug in Logic.",
                        value="Please contact the developer.(zion010928@gmail.com)", inline=False)
        embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                            icon_url='https://i.imgur.com/ltiu4g8.png')
        await ctx.send("Discord Bot Logic Error", embed=embed)

@bot.command(aliases = ['m'])
async def most(ctx):
    if ctx.author == bot.user:
        return
    try:
        if len(ctx.message.content.split(" ")) == 1:
            embed = discord.Embed(
                title="Summoner name not entered!", description="", color=0x5CD1E5)
            embed.add_field(name="Summoner name not entered",
                            value="To use command !recode : !recode (Summoner Nickname) \n To use command !most : !most (Summoner Nickname)", inline=False)
            embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                icon_url='https://i.imgur.com/ltiu4g8.png')
            await ctx.send("Summoner name not entered!", embed=embed)
        else:
            playerNickname = ' '.join((ctx.message.content).split(' ')[1:])
            getMasteryBox = apiCall.getPersonalChampionMasteries(
                playerNickname)
            keys = list(getMasteryBox.keys())
            if not getMasteryBox:
                embed = discord.Embed(
                    title="A non-existent summoner", description="", color=0x5CD1E5)
                embed.add_field(name="The summoner for this nickname does not exist.",
                                value="Please check the summoner's name.", inline=False)
                embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                    icon_url='https://i.imgur.com/ltiu4g8.png')
                await ctx.send("It's a summoner who doesn't exist.", embed=embed)
            else:
                embed = discord.Embed(
                    title=f"Summoner \"{playerNickname}\"\'s Most Top 3", description="", color=0x5CD1E5)
                embed.add_field(
                    name="Data Source", value="Data by Official Riot API : https://developer.riotgames.com/", inline=False)
                count = 1
                thumbnail = 'lorem ipsum'
                for i in getMasteryBox:
                    key = keys[count - 1]
                    p = getMasteryBox[key]
                    embed.add_field(
                        name=f"Most{count} : {key}", value=f"Proficiency Level : {p['championlevel']}.Lv / Champion Point : {p['championpoint']}pt", inline=False)
                    if count == 1:
                        thumbnail = p['championImage']
                    else:
                        pass
                    count += 1
                embed.set_thumbnail(
                    url=f"http://ddragon.leagueoflegends.com/cdn/11.13.1/img/champion/{thumbnail}")
                embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                                    icon_url='https://i.imgur.com/ltiu4g8.png')
                await ctx.send("Summoner \"" + playerNickname + "\"\'s Most Top3", embed=embed)
    except BaseException as e:
        embed = discord.Embed(title="A non-existent summoner",
                                description="", color=0x5CD1E5)
        embed.add_field(name="The summoner for this nickname does not exist.",
                        value="Please check the summoner's name.", inline=False)
        embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
                            icon_url='https://i.imgur.com/ltiu4g8.png')
        await ctx.send("It's a summoner who doesn't exist.", embed=embed)

# @bot.event
# async def on_message(ctx):  # on_message() event : when the bot has recieved a ctx
#     # To user who sent ctx
#     # await ctx.author.send(msg)

#     if ctx.author == bot.user:
#         return

#     if ctx.content.startswith("!help1") or ctx.content.startswith("!도움말1"):
#         embed = discord.Embed(
#             title="How to Use Commands", 
#             description="To use command !recode : !recode (Summoner Nickname) \n To use command !most : !most (Summoner Nickname)", color=0x5CD1E5)
#         embed.set_footer(text="LMB",
#                          icon_url='https://i.imgur.com/ltiu4g8.png')
#         await ctx.send(embed=embed)

#     if ctx.content.startswith("!recode"):
#         try:
#             if len(ctx.content.split(" ")) == 1:
#                 embed = discord.Embed(
#                     title="Summoner name not entered!", description="", color=0x5CD1E5)
#                 embed.add_field(name="Summoner name not entered",
#                                 value="To use command !recode : !recode (Summoner Nickname) \n To use command !most : !most (Summoner Nickname)", inline=False)
#                 embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                  icon_url='https://i.imgur.com/ltiu4g8.png')
#                 await ctx.send("Summoner name not entered!", embed=embed)
#             else:
#                 playerNickname = ' '.join((ctx.content).split(' ')[1:])
#                 # Return false if summoner not exist
#                 getPersonalRecordBox = apiCall.getPersonalGameRecord(
#                     playerNickname)
#                 if not getPersonalRecordBox:
#                     embed = discord.Embed(
#                         title="Non-existent summoner", description="", color=0x5CD1E5)
#                     embed.add_field(name="The summoner for this nickname does not exist.",
#                                     value="Please check the summoner's name.", inline=False)
#                     embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                      icon_url='https://i.imgur.com/ltiu4g8.png')
#                     await ctx.send("The summoner for this nickname does not exist.", embed=embed)
#                 else:
#                     record = getPersonalRecordBox["Record"]
#                     keys = record.keys()
#                     mastery = getPersonalRecordBox["ChampionMastery"]
#                     if len(record) == 2:
#                         solowinRatio = int((record['Personal/Duo Rank']['win'] / (
#                             record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank']['loss'])) * 100)
#                         flexwinRatio = int((record['Flex 5:5 Rank']['win'] / (
#                             record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
#                         solotier = record['Personal/Duo Rank']['tier']
#                         flextier = record['Flex 5:5 Rank']['tier']
#                         tc = tierCompare(solotier, flextier)
#                         thumbnail = "lorem ipsum"
#                         # Compare tier
#                         if tc == 0:
#                             thumbnail = solotier
#                         elif tc == 1:
#                             thumbnail = flextier
#                         else:
#                             thumbnail = solotier
#                         embed = discord.Embed(
#                             title="Summoner recode search", description="", color=0x5CD1E5)
#                         embed.add_field(name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['rank']}",
#                                         value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L / Win Ratio {solowinRatio}%", inline=False)
#                         embed.add_field(name=f"Flex 5:5 Rank : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['rank']}",
#                                         value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L / Win Ratio {flexwinRatio}%", inline=False)
#                         embed.add_field(
#                             name=f"Most Used Champion : {mastery['championname']}", value=f"Proficiency Level : {mastery['championlevel']}.Lv / Champion Point : {mastery['championpoint']}pt")
#                         embed.set_thumbnail(
#                             url=f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{thumbnail}.png?raw=true")
#                         embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                          icon_url='https://i.imgur.com/ltiu4g8.png')
#                         await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

#                     elif len(record) == 0:
#                         embed = discord.Embed(
#                             title="Summoner recode search", description="", color=0x5CD1E5)
#                         embed.add_field(name="Ranked Solo : Unranked",
#                                         value="Unranked", inline=False)
#                         embed.add_field(
#                             name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
#                         embed.set_thumbnail(
#                             url="https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_DEFAULT.png?raw=true")
#                         embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                          icon_url='https://i.imgur.com/ltiu4g8.png')
#                         await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

#                     elif len(record) == 1 and "Personal/Duo Rank" not in keys:
#                         flexwinRatio = int((record['Flex 5:5 Rank']['win'] / (
#                             record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
#                         embed = discord.Embed(
#                             title="Summoner recode search", description="", color=0x5CD1E5)
#                         embed.add_field(name="Ranked Solo : Unranked",
#                                         value="Unranked", inline=False)
#                         embed.add_field(name=f"Flex 5:5 Rank : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['rank']}",
#                                         value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L / Win Ratio {flexwinRatio}%", inline=False)
#                         embed.add_field(
#                             name=f"Most Used Champion : {mastery['championname']}", value=f"Proficiency Level : {mastery['championlevel']}.Lv / Champion Point : {mastery['championpoint']}pt")
#                         embed.set_thumbnail(
#                             url=f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{record['Flex 5:5 Rank']['tier']}.png?raw=true")
#                         embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                          icon_url='https://i.imgur.com/ltiu4g8.png')
#                         await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

#                     elif len(record) == 1 and "Flex 5:5 Rank" not in keys:
#                         solowinRatio = int((record['Personal/Duo Rank']['win'] / (
#                             record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank']['loss'])) * 100)
#                         embed = discord.Embed(
#                             title="Summoner recode search", description="", color=0x5CD1E5)
#                         embed.add_field(name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['rank']}",
#                                         value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L / Win Ratio {solowinRatio}%", inline=False)
#                         embed.add_field(
#                             name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
#                         embed.add_field(
#                             name=f"Most Used Champion : {mastery['championname']}", value=f"Proficiency Level : {mastery['championlevel']}.Lv / Champion Point : {mastery['championpoint']}pt")
#                         embed.set_thumbnail(
#                             url=f"https://github.com/zion928/Discord/blob/main/Ranked-emblems/Emblem_{record['Personal/Duo Rank']['tier']}.png?raw=true")
#                         embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                          icon_url='https://i.imgur.com/ltiu4g8.png')
#                         await ctx.send("Summoner \"" + playerNickname + "\"\'s recode", embed=embed)

#         except BaseException as e:
#             print(e)
#             embed = discord.Embed(title="There was a bug in Logic.",
#                                   description="", color=0x5CD1E5)
#             embed.add_field(name="There was a bug in Logic.",
#                             value="Please contact the developer.(zion010928@gmail.com)", inline=False)
#             embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                              icon_url='https://i.imgur.com/ltiu4g8.png')
#             await ctx.send("Discord Bot Logic Error", embed=embed)

#     if ctx.content.startswith("!most"):
#         try:
#             if len(ctx.content.split(" ")) == 1:
#                 embed = discord.Embed(
#                     title="Summoner name not entered!", description="", color=0x5CD1E5)
#                 embed.add_field(name="Summoner name not entered",
#                                 value="To use command !recode : !recode (Summoner Nickname) \n To use command !most : !most (Summoner Nickname)", inline=False)
#                 embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                  icon_url='https://i.imgur.com/ltiu4g8.png')
#                 await ctx.send("Summoner name not entered!", embed=embed)
#             else:
#                 playerNickname = ' '.join((ctx.content).split(' ')[1:])
#                 getMasteryBox = apiCall.getPersonalChampionMasteries(
#                     playerNickname)
#                 keys = list(getMasteryBox.keys())
#                 if not getMasteryBox:
#                     embed = discord.Embed(
#                         title="A non-existent summoner", description="", color=0x5CD1E5)
#                     embed.add_field(name="The summoner for this nickname does not exist.",
#                                     value="Please check the summoner's name.", inline=False)
#                     embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                      icon_url='https://i.imgur.com/ltiu4g8.png')
#                     await ctx.send("It's a summoner who doesn't exist.", embed=embed)
#                 else:
#                     embed = discord.Embed(
#                         title=f"Summoner \"{playerNickname}\"\'s Most Top 3", description="", color=0x5CD1E5)
#                     embed.add_field(
#                         name="Data Source", value="Data by Official Riot API : https://developer.riotgames.com/", inline=False)
#                     count = 1
#                     thumbnail = 'lorem ipsum'
#                     for i in getMasteryBox:
#                         key = keys[count - 1]
#                         p = getMasteryBox[key]
#                         embed.add_field(
#                             name=f"Most{count} : {key}", value=f"Proficiency Level : {p['championlevel']}.Lv / Champion Point : {p['championpoint']}pt", inline=False)
#                         if count == 1:
#                             thumbnail = p['championImage']
#                         else:
#                             pass
#                         count += 1
#                     embed.set_thumbnail(
#                         url=f"http://ddragon.leagueoflegends.com/cdn/11.13.1/img/champion/{thumbnail}")
#                     embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                                      icon_url='https://i.imgur.com/ltiu4g8.png')
#                     await ctx.send("Summoner \"" + playerNickname + "\"\'s Most Top3", embed=embed)
#         except BaseException as e:
#             embed = discord.Embed(title="A non-existent summoner",
#                                   description="", color=0x5CD1E5)
#             embed.add_field(name="The summoner for this nickname does not exist.",
#                             value="Please check the summoner's name.", inline=False)
#             embed.set_footer(text='Data by Official Riot API : https://developer.riotgames.com/',
#                              icon_url='https://i.imgur.com/ltiu4g8.png')
#             await ctx.send("It's a summoner who doesn't exist.", embed=embed)
bot.run(bottoken)

# bot.run(TOKEN)
