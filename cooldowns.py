import discord
from discord.ext import commands

from typing import Union
from datetime import datetime, timedelta

from database import DatabaseConnection

class Cooldown(object):

    def __init__(self, database: DatabaseConnection, on_cooldown: Union[str, discord.Embed] = None): 
        self._database = database
        if on_cooldown:
            self.on_cooldown = on_cooldown
        else:
            self.on_cooldown = discord.Embed(
                description = 'You are on cooldown, **{time}** {unit}(s) left.', 
                color = discord.Color.red()
            )

    def __repr__(self): return f'{self.__class__.__name__}: [{self._database._database} - table: cooldowns]'

    def __str__(self): return f'{self.__class__.__name__}({self._database._database})'

    @classmethod
    def _format_time(seconds: int):
        if seconds >= 7 * 24 * (60 ** 2): return (f'{seconds / 7 * 24 * (60 ** 2):.2f}', 'week')
        if seconds >= 24 * (60 ** 2): return (f'{seconds / 24 * (60 ** 2):.2f}', 'day')
        if seconds >= 60 ** 2: return (f'{seconds / 60 ** 2:.1f}', 'hour')
        if seconds >= 60: return (f'{seconds / 60:.1f}', 'minute')
        return 'second'

    def start(self, seconds: int):
        async def predicate(ctx):
            c = await self.is_on_cooldown(ctx.author, ctx.command)
            if c:
                time = self._format_time(c)
                if isinstance(self.on_cooldown, discord.Embed):
                    self.on_cooldown.description = self.on_cooldown.description.replace('{time}', time[0]).replace('{unit}', time[1])
                    await ctx.send(embed = self.on_cooldown)
                    return False
                self.on_cooldown.replace('{time}', time[0]).replace('{unit}', time[1])
                await ctx.send(self.on_cooldown)
                return False
            await self._database.execute(
                '''
                    DELETE FROM cooldowns WHERE user_id = $1 AND command = $2;
                    INSERT INTO cooldowns (user_id, command, timestamp, seconds) VALUES ($3, $4, $5, $6);
                ''', ctx.author.id, ctx.command.name, ctx.author.id, ctx.command.name, datetime.now(), seconds
            )
            return True
        return commands.check(predicate)

    async def is_on_cooldown(self, user: Union[discord.User, discord.Member], command: commands.Command) -> Union[bool, int]:
        data = await self._database.fetchrow("SELECT * FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)
        if data:
            future = data["timestamp"] + timedelta(seconds = data["seconds"])
            if datetime.now() <= future:
                timeleft = future - datetime.now()
                return timeleft.seconds + timeleft.days * (24 * 60 ** 2)
        return False