import discord
from discord.ext import commands

from typing import Union, Tuple
from datetime import datetime, timedelta
import asyncio

from .database import DatabaseConnection
from ..errors import CommandOnCooldown

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
    def _format_time(self, seconds: int) -> Union[str, Tuple[str, str]]:
        if seconds >= 7 * 24 * (60 ** 2): return (f'{seconds / 7 * 24 * (60 ** 2):.2f}', 'week')
        if seconds >= 24 * (60 ** 2): return (f'{seconds / 24 * (60 ** 2):.2f}', 'day')
        if seconds >= 60 ** 2: return (f'{seconds / 60 ** 2:.1f}', 'hour')
        if seconds >= 60: return (f'{seconds / 60:.1f}', 'minute')
        return (seconds, 'second')

    def check(self, seconds: int) -> commands.check:
        """Adds a cooldown for a user on a command (as a check)."""
        async def predicate(ctx): await self.add(seconds, ctx.author, ctx.command)
        return commands.check(predicate)

    async def add(self, seconds: int, user: Union[discord.User, discord.Member], command: commands.Command) -> None:
        """Adds a cooldown for a user on a command."""
        if await self.is_on_cooldown(user, command):
            raise CommandOnCooldown(f'Command \'{command.name}\' is already on cooldown for {user}.')
        await self._database.execute("DELETE FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)
        await self._database.execute("INSERT INTO cooldowns (user_id, command, timestamp, seconds) VALUES ($1, $2, $3, $4);", user.id, command.name, datetime.now(), seconds)

    async def reset(self, user: Union[discord.User, discord.Member], command: commands.Command) -> None:
        """Resets the cooldown for a user on a command."""
        await self._database.execute("DELETE FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)
    
    async def reset_all(self, user: Union[discord.User, discord.Member]) -> None:
        """Resets all the active cooldowns for a user."""
        await self._database.execute("DELETE FROM cooldowns WHERE user_id = $1;", user.id)

    async def get_time(self, user: Union[discord.User, discord.Member], command: commands.Command) -> Union[tuple, None]:
        """Get the value and the unit of the time remaining. Returns None if the user's not on cooldown."""
        c = await self.is_on_cooldown(user, command)
        if c:
            return self._format_time(c)

    async def is_on_cooldown(self, user: Union[discord.User, discord.Member], command: commands.Command) -> Union[int, None]:
        """Get the value in seconds of the time remaining. Returns None if the user's not on cooldown."""
        data = await self._database.fetchrow("SELECT * FROM cooldowns WHERE user_id = $1 AND command = $2;", user.id, command.name)
        if data:
            future = data["timestamp"] + timedelta(seconds = data["seconds"])
            if datetime.now() <= future:
                timeleft = future - datetime.now()
                return timeleft.seconds + timeleft.days * (24 * 60 ** 2)