import os
import random
import sys

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="milc.")

admins = [  329960504376426496, # yoav
            417610386871812098, # ori
            315068042910498816, # omer
            368039129348440085 # nir
        ]

with open("token.txt", 'r') as f:
    token = f.read()

@bot.event
async def on_ready():
    msg = sys.argv[1].replace('╥', ' ').replace('╙', "\n")
    for a in admins:
        m = await (await bot.fetch_user(a)).send(msg)
        await m.add_reaction(random.choice(["💥", "🚀", "🎉", "👯‍♂️", "🌚", "🈳", "🇮🇲"]))

    # os.system("python3.10 Server.py")

bot.run(token)