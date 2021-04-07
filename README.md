# dpy_cooldowns (BETA)

`dpy_cooldowns` is a module that allows you to create database cooldowns with discordpy & PostgreSQL (for now).

Here's the [documentation](https://docs.gabrieldahan.me/dpy-cooldowns/) (not available at the moment).

## Getting Started :

### Install and Import the module :
**Python 3.5.3 or higher.**

Installing the module :
```bash
~ git clone https://github.com/gabriel-dahan/dpy-cooldowns/
~ cd dpy-cooldowns/

# Linux / MacOS
~ python3 -m pip install -U .

# Windows 
~ py -3 -m pip install -U .
```
Importing the module :
```python
from dpy_cooldowns import psql # PostgreSQL support
from dpy_cooldowns import mysql # MySQL support (not available at the moment)
```

### Example Code :
```python
#### main.py ####
...
_database = psql.DatabaseConnection('database', 'user', 'host', 'password')
cooldown = psql.Cooldown(_database)

@cooldown.check(10) # 10 seconds cooldown
@bot.command()
async def foo(ctx):
    await ctx.send('Hello everyone !')
```

## Working with Cogs
You have to import the `psql.Cooldown()` variable from the file you instancied it.
```python
from discord.ext import commands
from <py_path> import cooldown

# Example
class MyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cooldown.check(10)
    @commands.command()
    async def foo(self, ctx):
        await ctx.send("Hi everyone !")

def setup(bot):
    bot.add_cog(MyCog(bot))
```
You can also add the instance to the bot variables :
```python
#### main.py ####
bot.cooldown = psql.Connection(...)

#### mycog.py ####

# With this method, you cannot use the cooldown.check() decorator.
# Instead, you'll have to use cooldown.add() inside the command.

# Example :
class MyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def foo(self, ctx):
        await self.bot.cooldown.add(10, ctx.author, ctx.command)
        await ctx.send("Hi everyone !")

def setup(bot):
    bot.add_cog(MyCog(bot))
```

## Simple Errors Handler
A command will raise the `dpy_cooldowns.errors.CommandOnCooldown` error if it is on cooldown, there's an example of a simple handler for it :
```python
from discord.ext import commands
import dpy_cooldowns

class ErrorsHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, dpy_cooldowns.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown.")
```
You can also show how much time is remaining by importing the `psql.Connection()` instance as shown above and by using the `psql.Connection().get_time()` method. It takes the author and the command as parameters and returns a tuple with the value and the unit of the time remaining.

```python
time = cooldown.get_time(ctx.author, ctx.command)

print(time[0]) # Ex. output : 12
print(time[1]) # Ex. output : second
```

*If you're liking the project, consider adding a star to promote it, thank you !*