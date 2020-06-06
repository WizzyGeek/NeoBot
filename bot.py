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
"""Korosensei. A discord Bot"""
__authour__ = "TEEN BOOM"
__copyright__ = "Copyright (C) 2020  TEEN BOOM"
__credits__ = ["TEEN BOOM", "Anvit Dadape"]

__version__ = "2.0.1"
__email__ = "ojasscodingG@gmail.com"
__license__ = "GNU GPL3"
__status__ = "Development"
#-----------standard-imports-----------#
import logging
import os
import psycopg2
import sys
import traceback
import json

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands
import praw

#-----------module-imports-----------#
# Pylint import error here, reason unknown
from cogs.Utilty.Context import DBContext
#from utility import ErrorHandler, rank_query, update, lvlup
#----------------------------------------#
logging.basicConfig(
    format='%(name)s:%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    "Class to hold all Bot vars"

    def __init__(self):
        try:
            self.token = str(os.environ['token'])  # Redunant
            self.DATABASE_URL = str(os.environ['DATABASE_URL'])
            self.reddit_id = str(os.environ['reddit_id'])
            self.reddit_secret = str(os.environ['reddit_secret'])
            self.config = {
                "welchannel": 583703372725747713,
                "log": 709339678863786084
            }
        except Exception:
            logger.warning(
                "Enviroment Variables don't contain credentials, seeking secret.json")
            try:
                with open("secret.json", "r") as reader:
                    self.data = json.loads(reader.read())
            except Exception:
                logger.error(
                    "secret.json not found | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
                # Sorry python lords, I couldn't do it gracefully without this.
                sys.exit()
            else:
                try:
                    self.creds = self.data['credentials']
                    self.token = self.creds['token']
                    self.dburl = self.creds['DATABASE_URL']
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
#----------------------------------------#


def _prefix_callable(bot, msg):
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
    #----------------------------------------#
    def __init__(self, ConfigObj):
        self.config = ConfigObj
        # shortcuts
        self.token = self.config.token
        self.dburl = self.config.dburl
        self.rid = self.config.rid
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
        self.DeleteTime = 10.0  # The time to wait before deleting message.
        # I am too lazy so here's the embeds
        self.GreenEmbed = discord.Embed(colour=discord.Colour.green())
        self.TealEmbed = discord.Embed(colour=discord.Colour.teal())
        self.BlueEmbed = discord.Embed(colour=discord.Colour.blue())
        self.BlurpleEmbed = discord.Embed(colour=discord.Colour.blurple())
        self.RedEmbed = discord.Embed(colour=discord.Colour.red())
        self.DarkRedEmbed = discord.Embed(colour=discord.Colour.dark_red())
        self.GoldEmbed = discord.Embed(colour=discord.Colour.gold())
        for filename in os.listdir('./cogs'):
            # dump the file in the folder and Voila!
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

    async def on_command_error(self, ctx, error):
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

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name='My students :-)', type=discord.ActivityType.watching, status=discord.Status.idle))
        logger.info(
            f"Bot:{self.user}, Status = Online, Intialisation successful!")
        for server in self.guilds:
            self.cur.execute(
                f"INSERT INTO prefix (id, prefix) VALUES ({server.id}, '$,.') ON CONFLICT DO NOTHING")
            self.conn.commit()
    #----------------------------------------#

    def get_guild_prefixes(self, guild, *, local_inject=_prefix_callable):
        proxy_msg = discord.Object(id=None)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)
    #----------------------------------------#

    def get_raw_guild_prefixes(self, guild_id):
        return self.prefixes.get(guild_id, ['$', '.'])
    #----------------------------------------#

    async def set_guild_prefixes(self, guild, prefixes):
        if not prefixes:
            self.cur.execute(
                f'UPDATE prefix SET prefix={None} WHERE id={guild.id}')
            self.conn.commit()
            self.prefixes[guild.id] = prefixes
            return True  # useful for set prefix command
        elif len(prefixes) > 10:
            return False
        else:
            self.cur.execute('UPDATE prefix SET prefix=? WHERE id=?',
                             (','.join(sorted(set(prefixes))), str(guild.id)))
            self.conn.commit()
            self.prefixes[guild.id] = sorted(set(prefixes))
            return True
    #----------------------------------------#

    async def get_context(self, message, *, cls=DBContext):
        # when you override this method, you pass your new Context
        # subclass to the super() method, which tells the bot to
        # use the new MyContext class
        return await super().get_context(message, cls=cls)
    # Quick embed

    def Qembed(self, ctx, Colour=None, title: str = None, content: str = None, NameValuePairs: list = None):
        """
        A method to quickly create embeds

        embed = self.bot.Qembed(ctx, title="test", content = "passed", NameValuePairs = [("this is the first name", "this is the 1st value"),("this is the 2nd name", "this is the 2nd value")] )
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

    async def on_member_join(self, member):
        if member.Guid.id == 583689248117489675:  # Change this to enable welcoming also change these strings!
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
        logger.info("Logging in...")
        super().run(self.token, reconnect=True)

#--------------------------------------------------------------------------------#
if __name__ == '__main__':
    Config = Config()
    korosensei = Bot(Config)
    korosensei.run()
#------------------------------------------------------------------------------------------------------------------------#
