# dpy-psql-cooldowns (BETA)

`dpy-psql-cooldowns` is a module that allows you to create database cooldowns with discordpy & PostgreSQL (for now).

Here's the [documentation](https://docs.gabrieldahan.me/dpy-psql-cooldowns/) (not available at the moment).

## Examples :

```python
db = cooldowns.DatabaseConnection('database', 'user', 'host', 'password')

cooldown = cooldowns.Cooldown(db)

@cooldown.check(10) # 10 seconds
@bot.command(name = 'foo')
async def foo(ctx):
    await ctx.send('Test')
```

Default `on_cooldown` error message is :

![OnCooldown](https://imgur.com/t06bKYT.png)

To edit it, just add a string or a discord.Embed object as a parameter in the Cooldown object.

Example :
```python
embed = discord.Embed(
    description = 'Please wait ! There are {time} {unit}(s) left before you can re-execute this command.'
)
db = cooldowns.DatabaseConnection('database', 'user', 'host', 'password')

cooldown = cooldowns.Cooldown(db)

@cooldown.check(10, on_cooldown = embed) # on_cooldown error message will be 'embed' 
@bot.command(name = 'foo')
async def foo(ctx):
    await ctx.send('Test')
``` 

Note that ``{time}`` is used to show the time left and ``{unit}`` the unit corresponding to the remaining time. 

Ex : ``'{time} {unit}(s)'`` --> ``'13.5 second(s)'``