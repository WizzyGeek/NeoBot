#-----------standard-imports-----------#
import asyncio
import logging
import os
import psycopg2
import random
from string import punctuation
import traceback

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands

#-----------module-imports-----------#
#from utility import ErrorHandler, rank_query, update, lvlup

#----------------------------------------#
logging.basicConfig(format = '%(name)s:%(levelname)s: %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)
try:
    configToken = str(os.environ['Token'])
    DATABASE_URL = str(os.environ['DATABASE_URL'])
except Exception as err:
    logger.error("Config vars inaccessible!", exc_info = True) # exception avoided on purpose.
    logger.warning("datbase is URL not found")
    configToken = "token"
    DATABASE_URL = "url"
    logger.info("Alternate login token, id used.")

guild = discord.Guild
config = {"welchannel": 583703372725747713}
logger.info("Initialised config variables.")

conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()

try:
    c.execute("CREATE TABLE IF NOT EXISTS prefix(id BIGINT NOT NULL UNIQUE, prefix TEXT NOT NULL)")
    c.execute
    conn.commit()
except:
    logger.exception("Config vars inaccessible!")

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

class Bot(commands.Bot):
    def __init__(self, token):
        super().__init__(command_prefix=_prefix_callable,
                         description="Assassinations's discord bot")
        self.prefixes = {int(k): v.split(',') for (k, v) in pre.items()}
        self.token = configToken
        
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    bot.load_extension(f'cogs.{filename[:-3]}')
                except:
                    logger.exception(f"failed to initialise cog: {filename}")
                logger.info(f"Initialized cog: {filename}")
        logger.info("Initialised cogs and vars, running bot")
                
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)
            
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(name='My students :-)', type=discord.ActivityType.watching, status=discord.Status.idle))
        logger.info(f"Bot:{bot.user},Status = Online, Intialisation successful!")
        
    def get_guild_prefixes(self, guild, *, local_inject=_prefix_callable):
        proxy_msg = discord.Object(id=None)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)
    
     def get_raw_guild_prefixes(self, guild_id):
        return self.prefixes.get(guild_id, ['$', '.'])
    
    async def set_guild_prefixes(self, guild, prefixes):
           if not prefixes:
            c.execute('UPDATE prefix SET prefix=? WHERE id=?', (None, guild.id))
            conn.commit()
            self.prefixes[guild.id] = prefixes
        elif len(prefixes) > 15:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            c.execute('''UPDATE prefix
                         SET prefix=? 
                         WHERE id=?''',
                      (','.join(sorted(set(prefixes))), str(guild.id)))
            conn.commit()
            self.prefixes[guild.id] = sorted(set(prefixes))
            
    def run(self):
        logger.info("logging in process start")
        super().run(self.token, reconnect=True)

#----------------------------------------#
@bot.event
async def on_member_join(member):
    if member.Guid.id == 583689248117489675:
        logger.info(f"{member.name} intiated welcome process.")
        await member.send(f'Hi {member.name}, welcome to the Assassination Discord server!verify yoursel, read the rules and get some roles.')
        channel = bot.get_channel(config["welchannel"])
        embed = discord.Embed(title = "Welcome!", description = f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
        await channel.send(embed=embed, content=None)
    else:
        return
#--------------------------------------------------------------------------------#
if __name__ == '__main__':
    korosensei = Bot(configToken)
    korosensei.run()
#------------------------------------------------------------------------------------------------------------------------#