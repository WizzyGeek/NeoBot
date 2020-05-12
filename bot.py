#-----------standard-imports-----------#
import ast
import asyncio
import json
import logging
import os
import random
import re
import sys
import psycopg2
from collections import Counter
from math import floor, sqrt
from string import punctuation

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands
import requests

#-----------module-imports-----------#
#from utility import ErrorHandler, rank_query, update, lvlup

#----------------------------------------#
logging.basicConfig(format = '%(name)s:%(levelname)s: %(message)s', level = logging.INFO)
bot = commands.Bot(command_prefix="$")
logger = logging.getLogger(__name__)
try:
    configToken = str(os.environ['Token'])
    log = bot.get_channel(int(os.environ['log']))
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
    await member.send(f'Hi {member.name}, welcome to the Amazon Rainforest Discord server!')
    channel = bot.get_channel(config["welchannel"])
    embed = discord.Embed(title = "Welcome!", description = f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
    await channel.send(embed=embed, content=None)
#----------------------------------------#
@bot.command(aliases=['c', 'ch'])
async def chat(ctx, *, you):
    reply = str(grab_reply(you))
    await ctx.send(reply)
    #logger.info("Chat command requested!")

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
#The main function that will grab a reply
def grab_reply(question):
    #Navigate to the Search Reddit Url
    answers = requests.get('https://www.reddit.com/search.json?q=' + question + '&sort=relevance&t=all', headers = {'User-agent':'Small-Discord-chatbot-version-2.0.1.18'}).json
    Children = answers["data"]["children"]
    ans_list= []
    for post in Children:
        if post["data"]["num_comments"] >= 5:
            ans_list.append (post["data"]["url"])
        if len(ans_list) == 0:
            return "I have no idea"
    #Pick A Random Post
    comment_url = ans_list[random.randint(0,len(ans_list)-1)] + '.json?sort=top'    #Grab Random Comment Url and Append .json to end
    #Navigate to the Comments
    r = requests.get(comment_url, headers = {'User-agent': 'Chrome'})
    reply= json.loads(r.text)
    Children = reply[1]['data']['children']
    reply_list= []
    for post in Children:
        reply_list.append(post["data"]["body"])    #Add Comments to the List
    if len(reply_list) == 0:
        return "I have no clue"
    #Return a Random Comment
    reply = reply_list[random.randint(0,len(reply_list)-1)]
    return reply
#----------------------------------------#
def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
#----------------------------------------#

@sudo.command(name="eval")
async def eval_fn(ctx, *, cmd):
    """Evaluates input.
    Input is interpreted as newline seperated statements.
    If the last statement is an expression, that is the return value.
    Usable globals:
      - `bot`: the bot instance
      - `discord`: the discord module
      - `commands`: the discord.ext.commands module
      - `ctx`: the invokation context
      - `__import__`: the builtin `__import__` function
    Such that `>eval 1 + 1` gives `2` as the result.
    The following invokation will cause the bot to send the text '9'
    to the channel of invokation and return '3' as the result of evaluating
    >eval ```
    a = 1 + 2
    b = a * 2
    await ctx.send(a + b)
    a
    ```
    """
    fn_name = "_eval_expr"

    cmd = cmd.strip("` ")

    # add a layer of indentation
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    result = (await eval(f"{fn_name}()", env))
    await ctx.send(result)
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