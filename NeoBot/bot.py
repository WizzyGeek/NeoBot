# Korosensei, a Discord chatbot.
# Copyright (C) 2020  TEEN BOOM
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Requirments: requirements.txt
# &
# libopus
# ffmpeg
#
# Approximate Enviroment Size : 146 MiB
"""Korosensei. A discord Bot."""
import json
#-----------standard-imports-----------#
import importlib
import logging
import os
import pathlib
import platform
import signal
import sys
import traceback
import typing
from typing import Iterable, List, Tuple, Union, Dict, Optional

#-----------3rd-party-imports-----------#
import discord
import praw
import psycopg2
import wavelink
from discord.ext import commands

#-----------module-imports-----------#
from .Utils import Config, DBContext, _prefix_callable
#----------------------------------------#
try:
    import uvloop
except ImportError:
    pass
else:
    import asyncio
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if platform.system() == "Windows":
    asyncio.set_event_loop(asyncio.ProactorEventLoop())

logging.basicConfig(format="%(name)s:%(levelname)s: %(message)s", level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

gateway_logr: logging.Logger = logging.getLogger("discord.gateway").setLevel(logging.WARNING)

try:
    import timber
except ImportError:
    pass
else:
    try:
        with open("timber.json", "r") as reader:
            data: Dict[str, str] = json.load(reader)
    except FileNotFoundError:
        try:
            key: str = str(os.environ["KEY"])
            source_id: str = str(os.environ["ID"])
        except KeyError:
            logging.exception("Timber package installed but credentials not provided. Uninstall package if not needed.")
    else:
        key: str = data["key"]
        source_id: str = data["source"]

    timber_handler = timber.TimberHandler(
        source_id=source_id,
        api_key=key,
        raise_exceptions=True,
        drop_extra_events=False
        )
    logging.getLogger("").addHandler(timber_handler)

#----------------------------------------#


class Neo(commands.Bot):
    """
    Bot class with helper functions.
    
        Inherits all attributes from commands.Bot
        The attributes are:
        config
        token
        dburl (database url)
        rid (reddit id)
        rsecret (reddit secret)
        wavepass (Lavalink server"s password)
        log (The Guilds log channel soon to be changed)
        cur (The DB cursor)
        conn (The DB Connection)
        reddit_client
        Qembed
    """    

    def __init__(self, ConfigObj: Config, *, description: str = None, DeleteTime: float = 10.0, beta_indicator: str = "beta"):
        """Intialise the bot.
        
            Require a config object with info and credentials.

        Args:
            ConfigObj ([Config]):
                Object holding all info and credentials the bot requires
        """
        self.beta_indicator: str = beta_indicator
        super().__init__(command_prefix=_prefix_callable, description=description)
        # For testing...
        self.is_beta: bool = False

        self.DeleteTime: float = DeleteTime  # DESC: The time to wait before deleting message.
        self.config: Config = ConfigObj
        self.config.DB()
        # TODO: [Shorten code and remove unnecessary attrs]
        self.token = self.config.token
        self.dburl = self.config.dburl
        self.rid = self.config.rid
        self.wavepass = self.config.wavepass
        self.rsecret = self.config.rsecret
        self.log = int(self.config.config["log"])
        self.cur = self.config.cur
        self.conn = self.config.conn

        self.wavelink: wavelink.Client = wavelink.Client(bot=self)
        self.reddit_client: praw.Reddit = praw.Reddit(client_id=self.rid, client_secret=self.rsecret, user_agent="Small-post-seacrcher")

        self.cur.execute("SELECT * FROM prefix")
        self.prefixes: Dict[int, List[str]] = {int(id): prefixes.split(",") for (id, prefixes) in {entry[0]: entry[1] or "$,." for entry in self.cur.fetchall()}.items()}

        self.packaged_cogs = ["Connect4"]

        self.cog_dir: pathlib.Path = pathlib.Path(__file__).parent.absolute() / "cogs"
        for module in self.cog_dir.glob('*.py'):
            # REASON: [dump the file in the folder and Voila!]
            if module.name != "__init__.py":
                try:
                    name = module.stem
                    spec = importlib.util.spec_from_file_location(name, module)
                    self._load_from_module_spec(spec, name)
                    # self.load_extension(f"KorosenseiBot.cogs.{module[:-3]}")
                except:
                    logger.exception(f"Failed to initialise Cog | ⚙ | {name} at {module}")
                else:
                    logger.info(f"Initialized Cog | ⚙ | {name} at {module}")

        for package in list(map(lambda x: self.cog_dir.joinpath(pathlib.Path(x) / "__init__.py").absolute(), self.packaged_cogs)):
            try:
                name = package.parent.name
                spec = importlib.util.spec_from_file_location(name, package)
                self._load_from_module_spec(spec, name)
                # self.load_extension(package)
            except:
                logger.exception(f"Failed to initialise cog: {name} at {package}")
            else:
                logger.info(f"Initialized Cog | ⚙ | {name} at {package}")
        else:
            logger.info("Initialised Cogs | Running Bot ...")
    #----------------------------------------#
    async def _initialize(self) -> None:
        """Callled when bot is ready"""
        self.log = self.get_channel(self.log)
        await self._add_exit_handler()
    #----------------------------------------#

    async def on_command_error(self, ctx: commands.Context, error: discord.ext.commands.CommandError) -> None:
        """Event for all command errors.

        Args:
            ctx (commands.Context): The context
            error (discord.ext.commands.CommandError): The discord error
        """
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send("Sorry. This command is disabled and cannot be used.")
        elif isinstance(error, commands.CommandInvokeError):
            logger.error(f"In {ctx.command.qualified_name}:")
            traceback.print_tb(error.original.__traceback__)
            logger.error(
                f"{error.original.__class__.__name__}: {error.original}")
    #----------------------------------------#

    async def on_ready(self) -> None:
        """Bot event triggerred when the connection to discord has been established."""
        if self.beta_indicator in self.user.name.lower():
            self.is_beta = True # Dont put 'b e t a' in your bot name if it's not beta.

        act = "other Bots and you. 😃"
        if not self.is_beta:
            act = "My students 😃"
        await self.change_presence(activity=discord.Activity(name=act, type=discord.ActivityType.watching, status=discord.Status.idle))
        logger.info(
            f"Bot: {self.user} | Beta: {self.is_beta} | Intialisation successful!")
        for server in self.guilds: # Blocking at large scale
            self.cur.execute(
                f"INSERT INTO prefix (gid, prefix) VALUES ({server.id}, '$,.') ON CONFLICT DO NOTHING") 
            self.conn.commit()
        await self._initialize()
    #----------------------------------------#

    def get_guild_prefixes(self, guild: discord.Guild, *, local_inject=_prefix_callable) -> List[str]:
        """Return a list with guild prefixes.

        Args:
            guild (discord.Guild): The discord Guild
            local_inject (optional): A callable object returning the prefixes. Defaults to _prefix_callable.

        Returns:
            List[str]: [description]
        """        
        proxy_msg: discord.Object = discord.Object(id=None) # WET
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)
    #----------------------------------------#

    def get_raw_guild_prefixes(self, guild_id: int) -> List[str]:
        """Get default guild prefix.

        Args:
            guild_id (int): The id of the discord Guild.

        Returns:
            List[str]: List containing guild"s prefixes
        """                 
        return self.prefixes.get(guild_id, ["$", "."])
    #----------------------------------------#

    async def set_guild_prefixes(self, guild: discord.Guild, prefixes: List[str]) -> bool:
        """Set the guild prefix.

        Args:
            guild (discord.Guild): Any discord guild that the bot is a member of.
            prefixes (List[str]): List of prefixes that will be set as prefixes

        Returns:
            bool: True when succesful, False if not
        """        
        if not prefixes:
            self.cur.execute(
                f"UPDATE prefix SET prefix={None} WHERE id={guild.id}")
            self.conn.commit()
            self.prefixes[guild.id] = prefixes
            return True  # useful for set prefix command
        elif len(prefixes) > 13:
            return False
        else:
            self.cur.execute(f"UPDATE prefix SET prefix='{','.join(set(prefixes))}' WHERE gid={guild.id}")
            self.conn.commit()
            self.prefixes[guild.id] = sorted(set(prefixes))
            return True
    #----------------------------------------#

    async def get_context(self, message: discord.Message, *, cls: commands.Context = DBContext) -> DBContext:
        """Load DBContext object by default.

        Args:
            message (discord.Message): A discord message object.
            cls (commands.Context, optional): The Context class. Defaults to DBContext.

        Returns:
            DBContext: The over-ridden context object that this project uses.
        """        
        return await super().get_context(message, cls=cls)

    # Quick embed
    def Qembed(self, ctx: commands.Context, Colour:Union[int, str, Iterable[Union[str, int]]]=None, title: str = None, content: str = None, NameValuePairs: Iterable[Iterable[str]] = None) -> discord.Embed:
        """Quickly create embeds.

        Args:
            ctx (commands.Context): Context object
            Colour (Union[int, str, Iterable[Union[str, int]]], optional): 
                The colour defualts to author"s supports 1 : green, 2 : yellow, 3 : red,
                it supports any colour for that matter. Defaults to None.
            title (str, optional): The title. Defaults to None.
            content (str, optional): the description. Defaults to None.
            NameValuePairs (Iterable[Iterable[str]], optional): 2d iterables with dimension of (2, max(n, 25)). Defaults to None.

        Returns:
            discord.Embed: [description]
        """           
        if title is None:
            title = discord.Embed.Empty
        if content is None:
            content = discord.Embed.Empty
        if Colour is None:
            Colour = ctx.author.colour
        if Colour in [1, "1"]:
            Colour = discord.Colour.green()
        elif Colour in [2, "2"]:
            Colour = 0xFFD300
        elif Colour in [3, "3"]:
            Colour = discord.Colour.red()
        else:
            pass
        embed: discord.Embed = discord.Embed(title=title, description=content,
                              timestamp=ctx.message.created_at, colour=Colour)
        embed.set_footer(
            text=f"{str(ctx.author)}", icon_url=ctx.author.avatar_url)
        if NameValuePairs is not None:
            for pair in NameValuePairs:
                embed.add_field(name=pair[0], value=pair[1])
        return embed

    #----------------------------------------#

    async def on_member_join(self, member: discord.Member) -> None:
        """Greet a user in my server.

        Args:
            member (discord.Member): Discord member object.
        """        
        if member.guild.id == 583689248117489675 and not self.is_beta:  # Change this to enable welcoming also change these strings!
            logger.info(f"{member.name} intiated welcome process.")
            await member.send(f"Hi {member.name}, welcome to the Assassination Discord server! Verify yourself, read the rules and get some roles.")
            channel = self.get_channel(self.config.config["welchannel"])
            embed: discord.Embed = discord.Embed(
                title="Welcome!", description=f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
            await channel.send(embed=embed, content=None)
        else:
            return
    #----------------------------------------#

    def run(self) -> None:
        """Run the bot."""
        logger.info("Logging in...")
        super().run(self.token, reconnect=True)
        self.conn.close()
    #----------------------------------------#

    async def _close_(self) -> None:
        async def inner(client):
            Nodes = list(client.nodes.values())
            if Nodes: # Check if there are any.
                for node in Nodes:
                    await node.destroy()
            await client.session.close()
            logging.getLogger("wavelink.client").info(f"Closed session and destroyed Nodes.")
            return True
        try:
            # For discord's run method.
            self.loop.stop()
            # Let other tasks run.
            await inner(self.wavelink)
        except asyncio.CancelledError:
            await inner(self.wavelink)
    #----------------------------------------#

    async def _add_exit_handler(self) -> None:
        def wraper(*args): # signum and frame not needed
            self.loop.create_task(self._close_())
        try:
            await self.wait_until_ready()
            self.loop.add_signal_handler(signal.SIGINT, wraper)
            self.loop.add_signal_handler(signal.SIGTERM, wraper)
        except NotImplementedError:
            try:
                # We really want to close the websockets.
                # Windows doesn't support loop.add_signal_handler
                signal.signal(signal.SIGINT, wraper)
                signal.signal(signal.SIGTERM, wraper)
            except Exception:
                logger.warning("Failed to add wavelink exit handler.", exc_info=True)
                return
            else:
                logger.debug("Added wavelink signal handler.")
                return
        except Exception:
            logger.warning("Failed to add wavelink exit handler.", exc_info=True)
            return
        else:
            logger.debug("Added wavelink loop signal handler.")
            return

#--------------------------------------------------------------------------------#
if __name__ == "__main__":
    ConfigObj: Config = Config()
    korosensei: Bot = Bot(ConfigObj)
    korosensei.run()
#------------------------------------------------------------------------------------------------------------------------#
