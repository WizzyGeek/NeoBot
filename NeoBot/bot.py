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
#-----------standard-imports-----------#
import asyncio
import importlib
import json
import logging
import os
import pathlib
import platform
import signal
import sys
import traceback
import typing
from typing import Dict, Iterable, List, Optional, Tuple, Union, Any

#-----------3rd-party-imports-----------#
import discord
import praw
import psycopg2
import wavelink
from discord.ext import commands, tasks

#-----------module-imports-----------#
from .Utils import Config, NeoContext, _prefix_callable

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

logging.basicConfig(format="%(name)s:%(levelname)s: %(message)s", level=logging.INFO, datefmt="[%X]")
root_logger = logging.getLogger()

try:
    from rich.logging import RichHandler
except ImportError:
    pass
else:
    if str(os.environ["RICH"]).lower() in ["yes", "y", "true", "t"]:
        root_logger.removeHandler(root_logger.handlers[0])
        root_logger.addHandler(RichHandler())
        # Rich is present
        from rich.traceback import install
        install()
    # For tables in Future
    # rich_logs = True

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
            logging.info("Timber package installed but credentials not provided. Uninstall package if not needed.")
    else:
        key: str = data["key"]
        source_id: str = data["source"]

    timber_handler = timber.TimberHandler(
        source_id=source_id,
        api_key=key,
        raise_exceptions=True,
        drop_extra_events=False
        )
    root_logger.addHandler(timber_handler)

logger: logging.Logger = logging.getLogger(__name__)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

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
        DbPool (asyncpg)
    """

    def __init__(self, ConfigObj: Config, *, description: str = None, DeleteTime: float = 10.0, beta_indicator: str = "beta", **options):
        """Intialise the bot.
        
            Require a config object with info and credentials.

        Args:
            ConfigObj ([Config]):
                Object holding all info and credentials the bot requires
        """
        # FORMAT:: [f"{Entity} for {Reason}"]
        # NOTE:: [To Append credits from setup functions]
        self.credits: List[Union[Dict[str], str]] = [
            {
                "Entity": "TEEN-BOOM",
                "Reason": "Authoring the project"
            },
            {
                "Entity": "Anvit",
                "Reason": "Testing the bot"
            },
            {
                "Entity": "Vlad Carstocea",
                "Reason": "Contribution"
            }
        ]
        self._initialized = asyncio.Event()
        self.beta_indicator: str = beta_indicator
        super().__init__(command_prefix=_prefix_callable, description=description, **options)
        # -- |For testing...|
        self.is_beta: bool = False

        self.DeleteTime: float = DeleteTime  # DESC:: [The time to wait before deleting message]
        self.config: Config = ConfigObj
        self.GuildInfo = {}
        self.loop.create_task(self.__ainit__()) # -- Initialize the asyncpg pool when loop is started
        self.config.DB()                        # -- Initialize psycopg2 connection
        # TODO:: [Shorten code and remove unnecessary attrs]
        self.token = self.config.token
        self.dburl = self.config.dburl
        self.rid = self.config.rid
        self.wavepass = self.config.wavepass
        self.rsecret = self.config.rsecret
        self.cur = self.config.cur
        self.conn = self.config.conn

        self.wavelink: wavelink.Client = wavelink.Client(bot=self)
        self.reddit_client: praw.Reddit = praw.Reddit(client_id=self.rid, client_secret=self.rsecret, user_agent="Small-post-seacrcher")
    #----------------------------------------#
    async def __ainit__(self):
        """Async Constructor."""
        await self.config.__ainit__()
        self.DbPool = self.config.pool
        self.loop.create_task(self._load_config())
        self.prefixes: Dict[int, List[str]] = {int(entry[0]): entry[1].split(",") or "$,." for entry in await self.DbPool.fetch("SELECT * FROM prefix")}
        await self._load_internal_cogs()
    #----------------------------------------#
    async def _load_config(self):
        guilds = await self.DbPool.fetch("SELECT * FROM server")
        for guild in guilds:
            # print(guild)
            self.GuildInfo[guild[0]] = guild[1:2]
    #----------------------------------------#
    async def _load_internal_cogs(self):
        self.packaged_cogs = ["Connect4"]
        self.cog_dir: pathlib.Path = pathlib.Path(__file__).parent.absolute() / "cogs"
        for module in self.cog_dir.glob('*.py'):
            # REASON:: [dump the file in the folder and Voila!]
            if module.name != "__init__.py":
                try:
                    name = module.stem 
                    spec = importlib.util.spec_from_file_location(name, module)
                    self._load_from_module_spec(spec, name)
                except:
                    logger.exception(f"Failed to initialise Cog | ⚙ | {name} at {module}")
                else:
                    logger.info(f"Initialized Cog | ⚙ | {name} at {module}")

        for package in map(lambda x: self.cog_dir.joinpath(pathlib.Path(x) / "__init__.py").absolute(), self.packaged_cogs):
            try:
                name = package.parent.name
                spec = importlib.util.spec_from_file_location(name, package)
                self._load_from_module_spec(spec, name)
            except:
                logger.exception(f"Failed to initialise cog: {name} at {package}")
            else:
                logger.info(f"Initialized Cog | ⚙ | {name} at {package}")
        else:
            logger.info("Initialised Cogs | Running Bot ...")
        self._initialized.set()
    #----------------------------------------#
    async def _initialize(self) -> None:
        """Callled when bot is ready"""
        await self._add_exit_handler()
        async with self.DbPool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    f"INSERT INTO prefix (gid, prefix) VALUES ($1, '$,.') ON CONFLICT DO NOTHING", map(lambda guild: [guild.id], self.guilds))
        logger.info("Completed Bot Initialisation.")
    #----------------------------------------#

    async def on_command_error(self, ctx: commands.Context, error: discord.ext.commands.CommandError) -> None:
        """Event for all command errors.

        Args:
            ctx (commands.Context): The context
            error (discord.ext.commands.CommandError): The discord error
        """
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.invoked_with} requires {error.param.name} argument.")
            # await self.help_command.send_help issues with hardware rn.
        # -- Internal(ish) Errors
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("Sorry. This command is disabled and cannot be used.")
        elif isinstance(error, commands.CommandInvokeError):
            logger.error(f"In {ctx.command.qualified_name}:")
            traceback.print_tb(error.original.__traceback__)
            logger.error(
                f"{error.original.__class__.__name__}: {error.original}")
    #----------------------------------------#

    async def on_ready(self) -> None:
        """Bot event triggerred when the connection to discord has been established."""
        if self.beta_indicator in self.user.name.lower():
            self.is_beta = True # NOTE:: [Dont put 'b e t a' in your bot name if it's not beta.]

        act = "other Bots and you"
        if not self.is_beta:
            act = "my Development?"
        await self.change_presence(activity=discord.Activity(name=act, type=discord.ActivityType.watching, status=discord.Status.idle))
        logger.info(
            f"Bot: {self.user} | Beta: {self.is_beta} | Intialisation successful!")
        self.loop.create_task(self._initialize())
    #----------------------------------------#

    def get_guild_prefixes(self, guild: discord.Guild, *, local_inject=_prefix_callable) -> List[str]:
        """Return a list with guild prefixes.

        Args:
            guild (discord.Guild): The discord Guild
            local_inject (optional): A callable object returning the prefixes. Defaults to _prefix_callable.

        Returns:
            List[str]: [description]
        """        
        proxy_msg: discord.Object = discord.Object(id=None) # -- WET
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
            return True  # -- |useful for set prefix command|
        elif len(prefixes) > 13:
            return False
        else:
            self.cur.execute(f"UPDATE prefix SET prefix='{','.join(set(prefixes))}' WHERE gid={guild.id}")
            self.conn.commit()
            self.prefixes[guild.id] = list(set(prefixes))
            return True
    #----------------------------------------#

    async def get_context(self, message: discord.Message, *, cls: commands.Context = NeoContext) -> Union[NeoContext, commands.Context]:
        """Load NeoContext object by default.

        Args:
            message (discord.Message): A discord message object.
            cls (commands.Context, optional): The Context class. Defaults to NeoContext.

        Returns:
            NeoContext: The over-ridden context object that this project uses.
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
            NameValuePairs (Iterable[Iterable[str]], optional): 2d iterables with dimension of (2, min(n, 25)). Defaults to None.

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
        if not self.is_beta:  # NOTE:: [Change this to enable welcoming also change these strings!]
            if not (Id := self.GuildInfo.get(ctx.guild.id, None)):
                return
            if not Id[1]:
                return
            channel = self.get_channel()
            if not channel:
                return
            logger.debug(f"{member.name} intiated welcome process.")
            await member.send(f"Hi {member.name}, welcome to {ctx.guild.name}")
            embed: discord.Embed = discord.Embed(
                title="Welcome!",
                description=f"welcome to the server {member.mention}! Everyone please make them feel welcomed!",
                colour=discord.Colour.blue())
            await channel.send(embed=embed, content=None)
        else:
            return
    #----------------------------------------#
    # @tasks.loop(minutes=5)
    # async def status_loop(self):
    #     act = next(self.status)
    #     await self.change_presence(activity=act)

    def run(self) -> None:
        """Run the bot."""
        logger.info("Logging in...")
        super().run(self.token, reconnect=True)
    #----------------------------------------#
    async def _close_(self) -> None:
        async def inner(bot: Neo):
            Nodes = list(bot.wavelink.nodes.values())
            if Nodes: # Check if there are any.
                for node in Nodes:
                    await node.destroy()
            await bot.wavelink.session.close()
            logging.getLogger("wavelink.client").info(f"Closed session and destroyed Nodes.")
            # -- Close asyncpg Pool
            self.conn.close()
            await bot.DbPool.close()
            logger.info("Closed Pool")
            logger.info("Exiting...")
            return True
        try:
            # REASON:: [For discord's run method.]
            self.loop.stop()
            # REASON:: [Let other tasks run.]
            await inner(self)
        except asyncio.CancelledError:
            await inner(self)
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
