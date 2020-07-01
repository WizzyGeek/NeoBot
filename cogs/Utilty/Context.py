"""Custom context class for discord."""
from typing import List, Union, Iterable, Optional

import discord
from discord.ext import commands

def CompareWithIterable(value, expr, iter: Iterable):
    """Compare an iterable with a single object to see if every element of iterable satifies expression."""
    for element in iter:
        if not expr(value, element):
            return element
        else:
            pass
    else:
        return True
    

class DBContext(commands.Context):
    """The over-rided context class."""

    def __init__(self, **kwargs):
        """Salt and peppa."""
        super().__init__(**kwargs)
        self.reddit_client = self.bot.reddit_client
        self.db = self.bot.conn
        self.cur = self.bot.cur
        self.target = set()
        self.set_target(self.message.mentions)

    def set_target(self, user: Union[Iterable[discord.Member], discord.Member] = None) -> None:
        """Set the commands target user.

        Args:
            user (Union[Iterable[discord.Member], discord.Member], optional): Set the target of a command. Defaults to None.
        """
        if not isinstance(user, Iterable):
            self.target = [user]
        else:
            self.target = user

    def is_target(self, user: discord.Member = None) -> bool:
        """Check if author is the target.

        Args:
            user (discord.Member, optional): Set it to None to compare author and any mentioned person. Defaults to None.

        Returns:
            bool: True if author is the target
        """        
        if user is None:
            return self.author in self.target

        return self.author == user

    def is_above(self, user: discord.Member = None) -> bool:
        """Check if author is above target.

        Args:
            user (discord.Member, optional): the target. Defaults to self.target[0]

        Returns:
            bool: True if author above target
        """
        if user is None:
            user = self.target
        if self.author == self.guild.owner:
            return True
        if user is not None:
            x = lambda z, y: z > y.top_role
            res = CompareWithIterable(self.author.top_role, x, user)
            if res == True:
                return res
            else:
                return res

    async def whisper(self, user: Union[discord.Member, List[discord.Member]] = None, *args, **kwargs) -> None:
        """DM all targets of a command.

        Args:
            user Optional(Union[discord.Member, List[discord.Member]]): The member(s) to DM. Defaults to self.target.

        Returns:
            [None]
        """                      
        if user is None:
            user = self.target
        if not isinstance(user, Iterable):
            return await user.send(*args, **kwargs)
        else:
            for target in user:
                target.send(*args, **kwargs)

    async def send(self, content=None, **kwargs) -> discord.Message:
        """Convert all messages outbound from the bot to Blurple Embed."""
        if content is not None and kwargs.pop("embed", None) is None:
            embed = embed = discord.Embed(description=content, colour=0x4e5d94) # Blurple | imports eat resources
            return await super().send(embed=embed, **kwargs)
        else:
            return await super().send(content=content, **kwargs)

    async def send_embed(self, *args, **kwargs) -> discord.Message:
        return await self.send(embed=discord.Embed(*args, **kwargs))
