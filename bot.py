# TOKEN = 'MTAzNjI1NzQ1MDgwODA2MjAxMg.GUjER1.r_5X7ILj_9FKiDZdXxCjg52wR1RSIXMu20U6rY'

import discord
from discord.ext import commands
import asyncio
from to import *
from date import *
# from opgg import *

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)  # 명령어 시작은 !


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-------')


@bot.command()
async def ping(ctx):  # !ping 입력시
    await ctx.send('pong')  # ctx = context 호출


@bot.command()
async def test(ctx, *, arg):  # arg = argument 매개변수
    await ctx.send(arg)


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(
        title="타이틀에 넣을 내용",
        description="설명에 넣을 내용",
        colour=0x62c1cc
        # ** 굵게 ** ' 작은 글씨 '
    )
    embed.add_field(
        name="필드의 이름",
        value="필드의 값"
    )
    # inline
    # false 가로 붙이기

    embed.set_footer(
        text=f"{ctx.message.author.name}",
        icon_url=ctx.message.author.avatar.url
        )
    # 꼬리말 / 보통 입력한 사용자의 닉네임, 프로필 사진 추가
    # 혹은 원하는 프로필 정보
    # text = f"{ctx.message.author.name}"
    # icon_url = ctx.message.author.avatar.url
    await ctx.send(embed=embed)


bot.run(TOKEN)
