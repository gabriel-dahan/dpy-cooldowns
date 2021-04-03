import discord
from discord.ext import commands

from dpy_cooldowns.psql import DatabaseConnection, Cooldown

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = ".", intents = intents)

_database = DatabaseConnection('database', 'user', 'host', 'password')
cooldown = Cooldown(_database)

@bot.event
async def on_ready():
    print('Ready !')

@cooldown.check(20)
@bot.command(name = 'foo')
async def foo(ctx):
    await ctx.send('Not on cooldown.')

bot.run('token')