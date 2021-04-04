from discord.ext import commands

class CommandOnCooldown(commands.CheckFailure):
    def __init__(self, error): self.error = error