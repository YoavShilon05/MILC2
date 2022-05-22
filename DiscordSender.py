import os
import sys

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="")

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
    msg_ids = []
    for a in admins:
        m = await (await bot.fetch_user(a)).send(msg)
        await m.add_reaction(":boom:")
        msg_ids.append(m.id)

    r = await bot.wait_for('on_reaction_add', check=lambda r, u: u.id in admins and r.message.id in msg_ids and r.emoji.name == ":boom:", timeout=10 * 60)
    if r is None:
        return

    for a in admins:
        await (await bot.fetch_user(a)).send("Restarting Server...")

    os.system("python3.10 Server.py")

bot.run(token)