import discord
from discord.ext import commands

class DBContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reddit_client = self.bot.reddit_client
        self.db = self.bot.conn
        self.cur = self.bot.cur

    def is_target(self, user: discord.abc.User) -> bool:
        """
        args:
            user: discord.abc.User
        returns:
            bool
        evaluates:
            ctx.author == user
        """
        return self.author == user

    def is_above(self, user: discord.Member) -> bool:
        """
        args:
            user: discord.abc.User
        returns:
            bool
        evaluates:
            ctx.author.top_role > user.top_role 
        """
        return self.author.top_role > user.top_role or self.author == self.guild.owner