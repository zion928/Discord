# TOKEN = 'MTAzNjI1NzQ1MDgwODA2MjAxMg.GUjER1.r_5X7ILj_9FKiDZdXxCjg52wR1RSIXMu20U6rY'

import discord
from discord.ext import commands
import asyncio
from to import *
from date import *
# from opgg import *

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents) # 명령어 시작은 !


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-------')

@bot.command()
async def ping(ctx): # !ping 입력시
    await ctx.send('pong') # ctx = context 호출

@bot.command()
async def test(ctx, *, arg): # arg = argument 매개변수
    await ctx.send(arg)

bot.run(TOKEN)