from collections.abc import Iterable
from typing import List, Union

import discord
from discord.ext import commands


class DBContext(commands.Context):
    """The over-rided context class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reddit_client = self.bot.reddit_client
        self.db = self.bot.conn
        self.cur = self.bot.cur
        self.target = self.message.mentions

    @property
    def set_target(self, *user: discord.Member):
        """
        set the target user
        """
        self.target = user

    def is_target(self, user: discord.Member = None) -> bool:
        """
        args:
            user: discord.abc.User
        returns:
            bool
        evaluates:
            ctx.author == user
        """
        if user is None:
            return self.author in self.target

        return self.author == user

    def is_above(self, user: discord.Member = None) -> bool:
        """
        args:
            user: discord.abc.User
        returns:
            bool
        evaluates:
            ctx.author.top_role > user.top_role 
        """
        if user is None:
            user = self.target[0]    # better than nothing
        return self.author.top_role > user.top_role or self.author == self.guild.owner

    async def whisper(self, user: List[Union[discord.Member, discord.User]] = None, *args, **kwargs):
        """
        DM (all) target(s) of a command
        args:
            user: List[Union[discord.Member, discord.User]] - optional
            content: str
            *All arguments send() method accepts*
        """      
        if user is None:
            user = self.target
        if not isinstance(user, Iterable):
            return await user.send(*args, **kwargs)  # make it iterable
        else:
            for target in user:
                target.send(*args, **kwargs)
