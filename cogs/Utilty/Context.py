import discord
from discord.ext import commands

class DBContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reddit_client = self.bot.reddit_client
        self.db = self.bot.conn
        self.cur = self.bot.cur

    def is_target(self, user: discord.User or discord.Member) -> bool:
        """
        args:
            user: discord.User or discord.Member
        returns:
            bool
        evaluates:
            ctx.author == user
        """
        return self.author == user