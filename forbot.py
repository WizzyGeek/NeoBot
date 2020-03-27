#-----------standard-imports-----------#
import ast
import asyncio
import logging
import os
import random
import re
import sqlite3
import sys
import psycopg2
from collections import Counter
from math import floor, sqrt
from string import punctuation

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands

#-----------module-imports-----------#
from utility import ErrorHandler, rank_query, update, lvlup

#----------------------------------------#
os.environ['DATABASE_URL'] = r"postgres://ovspnqbhsmynra:c5e500bb4fe1263ac459911d6461c02683a53ddb2467be4d48f040d7780eb041@ec2-54-197-34-207.compute-1.amazonaws.com:5432/d58tqf1iup8t6e"
logging.basicConfig(format = '%(name)s:%(levelname)s: %(message)s', level = logging.INFO)
bot = commands.Bot(command_prefix="$")
logger = logging.getLogger(__name__)
try:
    DATABASE_URL = os.environ['DATABASE_URL']
    configToken = str(os.environ['Token'])
    log = bot.get_channel(int(os.eviron['log']))
except Exception as err:
    logger.error("Config vars inaccessible!", exc_info = True) # exception avoided on purpose.
    logger.warning("If datbase is URL not found leveling system will crash!")
    configToken = 'NjQ3MDgxMjI2OTg4OTQ1NDIw.Xd-dYw.gyJH0ZJonpyjoRm1UttTNOrZ7_s'
    log = bot.get_channel(616955019727732737)
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
    else:
        await update(message=message)
    return None
#----------------------------------------#
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name='The Rainforests', type=discord.ActivityType.watching, status = discord.Status.idle))
    logger.info(f"Bot:{bot.user},Status = Online, Intialisation successful!")
#----------------------------------------#
@bot.event
async def on_member_join(member):
    logger.info(f"{member.name} intiated welcome process.")
    await member.send(f'Hi {member.name}, welcome to the Amazon Rainforest Discord server!')
    channel = bot.get_channel(config["welchannel"])
    embed = discord.Embed(title = "Welcome!", description = f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
    await channel.send(embed=embed, content=None)
#----------------------------------------#
@bot.command(aliases=['c', 'ch'])
async def chat(ctx, *, you):
    await ctx.send("Under Devlopment! sorry for any inconvenience caused.")
    logger.info("Chat command requested!")
    
@bot.command(name="report")
async def report(ctx, user, reason="Not given"):
    try:
        name = user.name
    except Exception:
        name = user
    author = ctx.author
    await author.send(f"Reported {user}!\nThe staff look into your matter soon.\nDon't use this feature as spam.")
    await ctx.message.delete()
    channel = bot.get_channel(int(620203303736836096))
    await channel.send(embed=discord.Embed(title="Report",description=f"{author} reported {name}\nreason:{reason}",colour=0x39ff14))
    return None
#----------------------------------------#
@bot.group()
@commands.has_permissions(administrator = True)
async def sudo(ctx):
    logging.info(f"elevated privilage use detected, USER : {ctx.author.name}")
    return None
#----------------------------------------#
@sudo.command(name="load")
@commands.is_owner()
async def load(ctx, extension):
    """loads a cog"""
    bot.load_extension(f"cogs.{extension}")
    logger.info(f"Loaded Cog {extension}")
    await ctx.send(embed=discord.Embed(title="Done",description=f"loaded {extension}"))
#----------------------------------------#
@sudo.command(name="reload")
@commands.is_owner()
async def reload(ctx, *, extension):
    """reloads a cog"""
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    logger.info(f"Reloaded Cog {extension}")
    await ctx.send(embed=discord.Embed(title="Done",description=f"Reloaded {extension}"))
#----------------------------------------#
@sudo.command(name="unload")
@commands.is_owner()
async def unload(ctx, extension):
    """unloads a cog"""
    bot.unload_extension(f"cogs.{extension}")
    logger.info(f"unloaded Cog {extension}")
    await ctx.send(embed=discord.Embed(title="Done",description=f"unloaded {extension}", colour = 0x00eb04))
#----------------------------------------#
@sudo.command(name="evalm")
async def evalpy(ctx, *, expr):
    """evaluates by parsing a pythonic expression"""
    str(expr)
    expr.replace("```", "")
    try:
        await ctx.send(ast.literal_eval(expr))
    except discord.errors.HTTPException:
        await ctx.send("executed but no string to send")
    except SyntaxError as err:
        await ctx.send(str(err) + "\n *note: single backticks not supported*")
    except discord.ext.commands.errors.MissingRequiredArgument:
        await ctx.send("umm, what to process?")
    except ValueError:
        await ctx.send(f"i dont know what you did but,\n{expr}\nis not allowed")
#----------------------------------------#
@sudo.command(name="dbdump")
@commands.is_owner()
async def dbdump(ctx):
    db = discord.File('chatbot.sqlite')
    try:
        await ctx.send(file=db, embed=discord.Embed(description = "here is the chat db", color = 0x576bde))
        logger.info("Chatbot DB Sent")
    except Exception:
        logger.exception("DB not sent, might be a fatal error")
    return None
#----------------------------------------#
@sudo.command(name="add_xp",aliases=["ax"])
async def add_xp(ctx, amount, user : discord.User=None):
    """Gives xp to a user"""
    if user is None:
        user = ctx.author
    User = user.id
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    cursor.execute(f"SELECT lvl, exp FROM level WHERE usr = {User}")
    res = cursor.fetchone()
    if res is not None:
        cursor.execute(f"UPDATE level SET exp=exp + {amount} WHERE usr = {User}")
        await ctx.send(embed=discord.Embed(title="Done", description=f"Gave {user.name},{amount} experience points!", color=0x32CD32))
        connection.commit()
        await lvlup(ctx, User)
        connection.close()
        return
    else:
        cursor.execute("SELECT MAX(id) FROM level")
        res = cursor.fetchone()
        if res == None:
            print(res)
            res = 0
        elif res != None:
            if res[0] == None:
                new_id = 1
            else:
                new_id = int(res[0]) + 1
        cursor.execute(f"INSERT INTO level VALUES({new_id}, {User}, 1, {amount})")
        connection.commit()
        connection.close()
        await lvlup(ctx, User)
#----------------------------------------#
@sudo.command(name="restart", aliases=['reboot'],description="restarts the entire bot")
@commands.is_owner()
async def reboot(ctx):
    logger.info(f"[IMP]Reboot request from {ctx.author.name} received.")
    await bot.logout()
    await bot.login(configToken)
    return None

#--------------------------------------------------------------------------------#
if __name__ == '__main__':
    runner()
#------------------------------------------------------------------------------------------------------------------------#