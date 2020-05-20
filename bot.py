#-----------standard-imports-----------#
import asyncio
import logging
import os
import random
from string import punctuation

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands

#-----------module-imports-----------#
#from utility import ErrorHandler, rank_query, update, lvlup

#----------------------------------------#
logging.basicConfig(format = '%(name)s:%(levelname)s: %(message)s', level = logging.INFO)
bot = commands.Bot(command_prefix="$")
logger = logging.getLogger(__name__)
try:
    configToken = str(os.environ['Token'])
except Exception as err:
    logger.error("Config vars inaccessible!", exc_info = True) # exception avoided on purpose.
    logger.warning("If datbase is URL not found leveling system will crash!")
    configToken = 'NjE5ODk2OTcyMTUyOTMwMzA4.XrqbXw.I3umpJzG7m1L8Yp7wDtepFi0iEg'
    logger.info("Alternate login token, id used.")

guild = discord.Guild
config = {"welchannel": 583703372725747713}
logger.info("Initialised config variables.")

def runner():
    logger.info("logging in process start")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f"Initialized cog: {filename}")
        else:
            pass
    logger.info("Initialised cogs and vars, running bot")
    try:
        bot.run(configToken)
    except Exception:
        logger.critical("Bot initialisation Unsuccessful! Program Exit/crash imminent!", exc_info = True)
#----------------------------------------#
@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)

    if message.author.bot:
        return None
    elif isinstance(message.channel, discord.abc.PrivateChannel):
        return None
    elif ctx.valid:
        await bot.process_commands(message)
        
    return None
#----------------------------------------#
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name='My students :-)', type=discord.ActivityType.watching, status=discord.Status.idle))
    logger.info(f"Bot:{bot.user},Status = Online, Intialisation successful!")
#----------------------------------------#
@bot.event
async def on_member_join(member):
    logger.info(f"{member.name} intiated welcome process.")
    await member.send(f'Hi {member.name}, welcome to the Assassination Discord server!verify yoursel, read the rules and get some roles.')
    channel = bot.get_channel(config["welchannel"])
    embed = discord.Embed(title = "Welcome!", description = f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
    await channel.send(embed=embed, content=None)
#--------------------------------------------------------------------------------#
if __name__ == '__main__':
    runner()
#------------------------------------------------------------------------------------------------------------------------#