import discord
from discord.ext import commands

import cooldowns

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = ".", intents = intents)

db = cooldowns.DatabaseConnection('database', 'user', 'host', 'password')
cooldown = cooldowns.Cooldown(db)

@bot.event
async def on_ready():
    print('Ready !')

@cooldown.start(20)
@bot.command(name = 'foo')
async def foo(ctx):
    await ctx.send('Not on cooldown.')

bot.run('token')