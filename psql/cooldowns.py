import discord
from discord.ext import commands

from typing import Union, Tuple
from datetime import datetime, timedelta
import asyncio

from database import DatabaseConnection

class Cooldown(object):

    def __init__(self, database: DatabaseConnection):
        self._database = database
        
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._database.execute(
            '''
                CREATE TABLE IF NOT EXISTS cooldowns(
                    user_id bigint,
                    command varchar(255),
                    timestamp timestamp,
                    seconds integer
                );
            '''
        ))

    def __repr__(self): return f'{self.__class__.__name__}: [{self._database._database} - table: cooldowns]'

    def __str__(self): return f'{self.__class__.__name__}({self._database._database})'

    @classmethod
    def _format_time(seconds: int) -> Union[str, Tuple[str, str]]:
        if seconds >= 7 * 24 * (60 ** 2): return (f'{seconds / 7 * 24 * (60 ** 2):.2f}', 'week')
        if seconds >= 24 * (60 ** 2): return (f'{seconds / 24 * (60 ** 2):.2f}', 'day')
        if seconds >= 60 ** 2: return (f'{seconds / 60 ** 2:.1f}', 'hour')
        if seconds >= 60: return (f'{seconds / 60:.1f}', 'minute')
        return 'second'

    def check(self, seconds: int, on_cooldown: Union[str, discord.Embed] = discord.Embed(description = 'You are on cooldown, **{time}** {unit}(s) left.', color = discord.Color.red())):
        async def predicate(ctx):
            c = await self.is_on_cooldown(ctx.author, ctx.command)
            if c:
                time = self._format_time(c)
                if isinstance(on_cooldow, discord.Embed):
                    on_cooldown.description = on_cooldown.description.replace('{time}', time[0]).replace('{unit}', time[1])
                    await ctx.send(embed = on_cooldown)
                    return False
                on_cooldown.replace('{time}', time[0]).replace('{unit}', time[1])
                await ctx.send(on_cooldown)
                return False
            await self._database.execute("DELETE FROM cooldowns WHERE user_id = $1 AND command = $2;", ctx.author.id, ctx.command.name)
            await self._database.execute("INSERT INTO cooldowns (user_id, command, timestamp, seconds) VALUES ($1, $2, $3, $4);", ctx.author.id, ctx.command.name, datetime.now(), seconds)
            return True
        return commands.check(predicate)

    async def add(self, seconds: int, user: Union[discord.User, discord.Member], command: commands.Command):
        if self.is_on_cooldown(user, command):
            raise CommandOnCooldown(f'Command \'{command.name}\' is already on cooldown for {user}.')
        await self._database.execute("DELETE FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)
        await self._database.execute("INSERT INTO cooldowns (user_id, command, timestamp, seconds) VALUES ($1, $2, $3, $4);", user.id, command.name, datetime.now(), seconds)

    async def reset(self, user: Union[discord.User, discord.Member], command: commands.Command):
        if self.is_on_cooldown(user, command):
            await self._database.execute("DELETE FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)

    async def is_on_cooldown(self, user: Union[discord.User, discord.Member], command: commands.Command) -> Union[bool, int]:
        data = await self._database.fetchrow("SELECT * FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)
        if data:
            future = data["timestamp"] + timedelta(seconds = data["seconds"])
            if datetime.now() <= future:
                timeleft = future - datetime.now()
                return timeleft.seconds + timeleft.days * (24 * 60 ** 2)
        return False

class CommandOnCooldown(Exception):

    def __init__(self, error): 
        self.error = error