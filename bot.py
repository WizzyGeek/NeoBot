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
__authour__ = "TEEN BOOM"
__copyright__ = "Copyright (C) 2020  TEEN BOOM"
__credits__ = ["TEEN BOOM", "Anvit Dadape"]

__version__ = "2.2.2a0"
__email__ = "ojasscoding@gmail.com"
__license__ = "GNU GPL3"
__status__ = "Development"
import json
#-----------standard-imports-----------#
import logging
import os
import sys
import traceback
import typing
from typing import Iterable, List, Tuple, Union

#-----------3rd-party-imports-----------#
import discord
import praw
import psycopg2
import wavelink
from discord.ext import commands

#-----------module-imports-----------#
from cogs.Utilty.Context import DBContext

#----------------------------------------#
logging.basicConfig(
    format='%(name)s:%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Config: # REASON: [Make it accessible on hover in ide.]
    """Collect all the required info.
        
            Requires a `secret.json` or envirment variables 
            and `lavalink.json` (optional) in the root directory.

        Args:
            MusicState (bool, optional):  Set the MusicState to false if Lavalink server is not available. Defaults to True.
    """
    
    def __init__(self, MusicState: bool = True):
        """Collect all the required info.
        
            Requires a `secret.json` or envirment variables 
            and `lavalink.json` (optional) in the root directory.

        Args:
            MusicState (bool, optional):  Set the MusicState to false if Lavalink server is not available. Defaults to True.
        """
        self.MusicState = MusicState
        try:
            self.token = str(os.environ['token'])  # Redunant but gives me peace of mind.
            self.dburl = str(os.environ['DATABASE_URL'])
            self.rid = str(os.environ['reddit_id'])
            self.rsecret = str(os.environ['reddit_secret'])
            self.config = {
                "welchannel": 583703372725747713,
                "log": 709339678863786084
            }
            self.wavepass = str(os.environ['wavepass'])
        except Exception:
            logger.warning(
                "Enviroment Variables don't contain credentials, seeking secret.json")
            try:
                with open("secret.json", "r") as reader:
                    self.data = json.loads(reader.read())
            except FileNotFoundError:
                logger.error(
                    "secret.json not found | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
                # Sorry python lords, I couldn't do it gracefully without this.
                sys.exit()
            except Exception:
                logger.exception("An unexpected error occured")
                sys.exit()
            else:
                try:
                    self.creds = self.data['credentials']
                    self.token = self.creds['token']
                    self.dburl = self.creds['DATABASE_URL']
                    self.wavepass = self.creds['wavepass']
                    self.reddit = self.data['reddit']
                    self.rid = self.reddit['id']
                    self.rsecret = self.reddit['secret']
                    self.config = self.data["config"]  # TODO: REMOVE THIS
                except KeyError:
                    logger.exception(
                        "secret.json not structured properly | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
                    sys.exit()
                except Exception:
                    logger.exception("An unexpected error occured")
                else:
                    logger.info("Credentials initialised")
        #----------------------------------------#
        try:
            self.conn = psycopg2.connect(self.dburl)
        except NameError:
            logger.exception("unexpected error occured!")
        except Exception:
            logger.exception("Cannot connect to postgre database")
        self.cur = self.conn.cursor()
        # logger.debug(f"Initialised config variables : {self.__dict__}") # Dangerous enable in secure condition only
        #----------------------------------------#
        try:
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS prefix(id BIGINT NOT NULL UNIQUE, prefix TEXT NOT NULL)")
            self.conn.commit()
        except:
            logger.exception("Psycopg2 error occured!")
        logger.info("Config Object initialised")
        
    @property
    def linkcreds(self) -> Union[dict, Exception, None]:
        """Fetch the lavalink credentials.
        
            A `lavalink.json` file is required in the root directory.
            

        Returns:
            Union[dict, Exception, None]: 
                Return None if MusicState is None, return error if an unexpected error occurs and return the dict if no errors were caught
        """        
        if self.MusicState:
            try:
                with open("lavalink.json", "r") as reader:
                    return json.loads(reader.read())
            except FileNotFoundError:
                logger.warning(
                    "lavalink.json not found continuing without music extension | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
            except Exception as err:
                logger.exception("An unexpected error occured")
                return err
        else:
            return None

        
#----------------------------------------#


def _prefix_callable(bot: commands.Bot, msg) -> List[str]:
    user_id = bot.user.id
    base = ['<@!{}> '.format(user_id), '<@{}> '.format(user_id)]
    if msg.guild is None:
        base.append('.')
        base.append('$')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['$', '.']))
    return base
#----------------------------------------#


class Bot(commands.Bot):
    """
    Bot class with helper functions.
    
        Inherits all attributes from commands.Bot
        The attributes are:
        config
        token
        dburl (database url)
        rid (reddit id)
        rsecret (reddit secret)
        wavepass (Lavalink server's password)
        log (The Guilds log channel soon to be changed)
        cur (The DB cursor)
        conn (The DB Connection)
        reddit_client
        Qembed
    """    

    def __init__(self, ConfigObj: Config):
        """Intialise the bot.
        
            Require a config object with info and credentials.

        Args:
            ConfigObj ([Config]):
                Object holding all info and credentials the bot requires
        """        
        self.config = ConfigObj
        # TODO: [Shorten code and remove unnecessary attrs]
        self.token = self.config.token
        self.dburl = self.config.dburl
        self.rid = self.config.rid
        self.wavepass = self.config.wavepass
        self.rsecret = self.config.rsecret
        self.log = self.config.config["log"]
        self.cur = self.config.cur
        self.conn = self.config.conn
        self.reddit_client = praw.Reddit(client_id=self.rid,
                                         client_secret=self.rsecret,
                                         user_agent="Small-post-seacrcher")
        super().__init__(command_prefix=_prefix_callable,
                         description="Assassinations's discord bot")
        self.cur.execute('SELECT * FROM prefix')
        prefix_rows = self.cur.fetchall()
        pre = {entry[0]: entry[1] or '!,?' for entry in prefix_rows}
        self.prefixes = {int(id): prefixes.split(',')
                         for (id, prefixes) in pre.items()}
        self.DeleteTime = 10.0  # DESC: The time to wait before deleting message.
        self.wavelink = wavelink.Client(bot=self)
        for filename in os.listdir('./cogs'):
            # REASON: [dump the file in the folder and Voila!]
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    self.load_extension(f'cogs.{filename[:-3]}')
                except:
                    logger.exception(f"failed to initialise cog: {filename}")
                else:
                    logger.info(f"Initialized cog: {filename}")
        else:
            logger.info("Initialised cogs and vars, running bot")
    #----------------------------------------#

    async def on_command_error(self, ctx: commands.Context, error: discord.ext.commands.CommandError) -> None:
        """Event for all command errors.

        Args:
            ctx (commands.Context): The context
            error (discord.ext.commands.CommandError): The discord error
        """
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            logger.error(f'In {ctx.command.qualified_name}:')
            traceback.print_tb(error.original.__traceback__)
            logger.error(
                f'{error.original.__class__.__name__}: {error.original}')
    #----------------------------------------#

    async def on_ready(self) -> None:
        """Bot event triggerred when the connection to discord has been established."""        
        await self.change_presence(activity=discord.Activity(name='My students :-)', type=discord.ActivityType.watching, status=discord.Status.idle))
        logger.info(
            f"Bot:{self.user}, Status = Online, Intialisation successful!")
        for server in self.guilds:
            self.cur.execute(
                f"INSERT INTO prefix (id, prefix) VALUES ({server.id}, '$,.') ON CONFLICT DO NOTHING") 
            self.conn.commit()
    #----------------------------------------#

    def get_guild_prefixes(self, guild: discord.Guild, *, local_inject=_prefix_callable) -> List[str]:
        """Return a list with guild prefixes.

        Args:
            guild (discord.Guild): The discord Guild
            local_inject (optional): A callable object returning the prefixes. Defaults to _prefix_callable.

        Returns:
            List[str]: [description]
        """        
        proxy_msg = discord.Object(id=None)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)
    #----------------------------------------#

    def get_raw_guild_prefixes(self, guild_id: int) -> List[str]:
        """Get default guild prefix.

        Args:
            guild_id (int): The id of the discord Guild.

        Returns:
            List[str]: List containing guild's prefixes
        """                 
        return self.prefixes.get(guild_id, ['$', '.'])
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
                f'UPDATE prefix SET prefix={None} WHERE id={guild.id}')
            self.conn.commit()
            self.prefixes[guild.id] = prefixes
            return True  # useful for set prefix command
        elif len(prefixes) > 13:
            return False
        else:
            self.cur.execute('UPDATE prefix SET prefix=? WHERE id=?',
                             (','.join(sorted(set(prefixes))), str(guild.id)))
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
                The colour defualts to author's supports 1 : green, 2 : yellow, 3 : red,
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
        if Colour in [1, '1']:
            Colour = discord.Colour.green()
        elif Colour in [2, '2']:
            Colour = 0xFFD300
        elif Colour in [3, '3']:
            Colour = discord.Colour.red()
        else:
            pass
        embed = discord.Embed(title=title, description=content,
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
        if member.guild.id == 583689248117489675:  # Change this to enable welcoming also change these strings!
            logger.info(f"{member.name} intiated welcome process.")
            await member.send(f'Hi {member.name}, welcome to the Assassination Discord server! Verify yourself, read the rules and get some roles.')
            channel = self.get_channel(self.config.config["welchannel"])
            embed = discord.Embed(
                title="Welcome!", description=f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
            await channel.send(embed=embed, content=None)
        else:
            return
    #----------------------------------------#

    def run(self):
        """Run the bot."""
        logger.info("Logging in...")
        super().run(self.token, reconnect=True)

#--------------------------------------------------------------------------------#
if __name__ == '__main__':
    ConfigObj = Config()
    korosensei = Bot(ConfigObj)
    korosensei.run()
#------------------------------------------------------------------------------------------------------------------------#
