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
import traceback
import json

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands

#-----------module-imports-----------#
#from utility import ErrorHandler, rank_query, update, lvlup
#----------------------------------------#
logging.basicConfig(
    format='%(name)s:%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
try:
    token = str(os.environ['token'])  # Redunant
    DATABASE_URL = str(os.environ['DATABASE_URL'])
    reddit_id = str(os.environ['reddit_id'])
    reddit_secret = str(os.environ['reddit_secret'])
except Exception:
    logger.warning(
        "Enviroment Variables don't contain credentials, seeking secret.json")
    try:
        with open("secret.json", "r") as reader:
            data = json.loads(reader.read())
    except Exception:
        logger.error(
            "secret.json not found | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
        quit()  # Sorry python lords, I couldn't do it gracefully without this.
    else:
        try:
            token = data['token']
            DATABASE_URL = data['DATABASE_URL']
            reddit_id = data['reddit']['id']
            reddit_secret = data['reddit']['secret']
        except KeyError:
            logger.error(
                "secret.json not structured properly | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
            quit()
        except Exception:
            logger.exception("An unexpected error occured")
        else:
            logger.info("Credentials initialised")
#----------------------------------------#
config = {
    "welchannel": 583703372725747713,
    "log": 709339678863786084
}
logger.info("Initialised config variables.")
#----------------------------------------#
try:
    conn = psycopg2.connect(DATABASE_URL)
except NameError:
    logger.exception("unexpected error occured!")
except Exception:
    logger.exception("Cannot connect to postgre database")
c = conn.cursor()
#----------------------------------------#
try:
    c.execute(
        "CREATE TABLE IF NOT EXISTS prefix(id BIGINT NOT NULL UNIQUE, prefix TEXT NOT NULL)")
    conn.commit()
except:
    logger.exception("Psycopg2 error occured!")


class Config:
    "Class to hold all Bot vars"

    def __init__(self, token=token, DATABASE_URL=DATABASE_URL, reddit_id=reddit_id, reddit_secret=reddit_secret):
        self.token = token
        self.dburl = DATABASE_URL
        self.rid = reddit_id
        self.rsecret = reddit_secret
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
    def __init__(self):
        self.config = Config()
        # shortcuts
        self.token = self.config.token
        self.dburl = self.config.dburl
        self.rid = self.config.rid
        self.rsecret = self.config.rsecret
        self.log = config["log"]
        super().__init__(command_prefix=_prefix_callable,
                         description="Assassinations's discord bot")
        c.execute('SELECT * FROM prefix')
        prefix_rows = c.fetchall()
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
            logger.exception("Fatal Error occured:")
            traceback.print_tb(error.original.__traceback__)
    #----------------------------------------#

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name='My students :-)', type=discord.ActivityType.watching, status=discord.Status.idle))
        logger.info(
            f"Bot:{self.user},Status = Online, Intialisation successful!")
        for server in self.guilds:
            c.execute(
                f"INSERT INTO prefix (id, prefix) VALUES ({server.id}, '$,.') ON CONFLICT DO NOTHING")
            conn.commit()
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
            c.execute(f'UPDATE prefix SET prefix={None} WHERE id={guild.id}')
            conn.commit()
            self.prefixes[guild.id] = prefixes
            return True  # useful for set prefix command
        elif len(prefixes) > 10:
            return False
        else:
            c.execute('UPDATE prefix SET prefix=? WHERE id=?',
                      (','.join(sorted(set(prefixes))), str(guild.id)))
            conn.commit()
            self.prefixes[guild.id] = sorted(set(prefixes))
            return True
    #----------------------------------------#
    # Quick embed

    async def Qembed(self, ctx, Colour=None, title: str = None, content: str = None, NameValuePairs: list = None):

        if t is None:
            t = discord.Embed.Empty
        if c is None:
            c = discord.Embed.Empty
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
                              timestamp=ctx.message.created_at)
        embed.set_footer(
            text=f"Requested by {str(ctx.author)}", icon_url=ctx.author.avatar_url)
        if NameValuePairs is not None:
            for pair in NameValuePairs:
                if pair[2] is True:
                    embed.add_field(name=pair[0], value=pair[1])
                elif pair[2] is False:
                    embed.add_field(name=pair[0], value=pair[1])
        return embed

    #----------------------------------------#

    async def on_member_join(self, member):
        if member.Guid.id == 583689248117489675:  # Change this to enable welcoming also change these strings!
            logger.info(f"{member.name} intiated welcome process.")
            await member.send(f'Hi {member.name}, welcome to the Assassination Discord server! Verify yourself, read the rules and get some roles.')
            channel = self.get_channel(config["welchannel"])
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
    korosensei = Bot()
    korosensei.run()
#------------------------------------------------------------------------------------------------------------------------#
