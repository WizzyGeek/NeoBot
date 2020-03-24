#-----------standard-imports-----------#
import ast
import asyncio
import logging
import os
import random
import re
import sqlite3
import psycopg2
from collections import Counter
from math import floor, sqrt
from string import punctuation

#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands

#-----------module-imports-----------#
from utils.utility import ErrorHandler, rank_query, update, lvlup

#----------------------------------------#
logging.basicConfig(filename = sys.stdout, format = '%(name)s:%(levelname)s: %(message)s', level = logging.INFO)
client = commands.Bot(command_prefix="$")
logger = logging.getLogger(__name__)
try:
    DATABASE_URL = os.environ['DATABASE_URL']
    configToken = str(os.environ['Token']) 
except Exception as err:
    logger.exception("Config vars inaccessible!")
    logger.critical("If datbase is URL not found leveling system will crash!")

if configToken is None:
    configToken = 'NjQ3MDgxMjI2OTg4OTQ1NDIw.Xd-dYw.gyJH0ZJonpyjoRm1UttTNOrZ7_s'
    logger.info("Alternate login token used.")

guild = discord.Guild
user = discord.Client()

config = {
    "welchannel": 583703372725747713
}
logger.info("Initialized config variables.")
#----------------------------------------#
@client.event
async def on_message(message):
    if message.author.bot:
        return None
    elif isinstance(message.channel, discord.abc.PrivateChannel):
        return None 
    else:
        await update(message=message)
    await client.process_commands(message)
    return None
#----------------------------------------#
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name='The Rainforests', type=discord.ActivityType.watching, status=discord.Status.idle))
    logger.info(f"Bot:{client.user},Status = Online")
#----------------------------------------#
@client.event
async def on_member_join(member):
    logger.info(f"{member.name} intiated welcome process.")
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to the Amazon Rainforest Discord server!')
    channel = client.get_channel(config["welchannel"])
    await channel.send(f"welcome to the server {member.mention}! everyone please make them feel welcomed!")
#----------------------------------------#
@client.command(aliases=['c', 'ch'])
async def chat(ctx, *, you):
    ctx.send("Under Devlopment! sorry for any inconvenience caused.")
    logger.info("Chat command requested!")
    """ connection = sqlite3.connect('chatbot.sqlite')
    cursor = connection.cursor()

    create_table_request_list = [
        'CREATE TABLE words(word TEXT UNIQUE)',
        'CREATE TABLE sentences(sentence TEXT UNIQUE, used INT NOT NULL DEFAULT 0)',
        'CREATE TABLE associations (word_id INT NOT NULL, sentence_id INT NOT NULL, weight REAL NOT NULL)',
    ]

    for create_table_request in create_table_request_list:
        try:
            cursor.execute(create_table_request)
        except:
            pass

    def get_id(entityName, text):
        tableName = entityName + 's'
        columnName = entityName
        cursor.execute('SELECT rowid FROM ' + tableName +
                       ' WHERE ' + columnName + ' = ?', (text,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            cursor.execute('INSERT INTO ' + tableName +
                           ' (' + columnName + ') VALUES (?)', (text,))
            return cursor.lastrowid

    def get_words(text):
        wordsRegexpString = r'(?:\w+|[' + re.escape(punctuation) + ']+)'
        wordsRegexp = re.compile(wordsRegexpString)
        wordsList = wordsRegexp.findall(text.lower())
        return Counter(wordsList).items()

    if you is None:
        print("ERROR: NO INPUT PROVIDED!")

    print(you)

    if you == '':
        await ctx.send("what?")
    elif you == 'bye':
        await ctx.send("bye")
        return
    else:
        pass

    cursor.execute(
        'CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
    words = get_words(you)
    words_length = sum([n * len(word) for word, n in words])

    for word, n in words:
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))

    cursor.execute(
        'SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    row = cursor.fetchone()
    cursor.execute('DROP TABLE results')

    if row is None:
        cursor.execute(
            'SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()

    Bot = row[1]
    cursor.execute(
        'UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))

    words = get_words(Bot)
    words_length = sum([n * len(word) for word, n in words])
    sentence_id = get_id('sentence', you)

    for word, n in words:
        word_id = get_id('word', word)
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO associations VALUES (?, ?, ?)',
                       (word_id, sentence_id, weight))

    connection.commit()
    await ctx.send(Bot) """

#----------------------------------------#
@client.group()
@commands.has_permissions(administrator = True)
async def sudo(ctx):
    logging.info(f"elevated privilage use detected, USER : {ctx.user.name}")
    return None
#----------------------------------------#
@sudo.command(name="load")
async def load(ctx, extension):
    """loads a cog"""
    client.load_extension(f"cogs.{extension}")
    print("loaded " + extension)
    await ctx.send("loaded")
#----------------------------------------#
@sudo.command(name="reload")
async def reload(ctx, *, extension):
    """reloads a cog"""
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    print("reloaded " + extension)
    await ctx.send("reloaded!")
#----------------------------------------#
@sudo.command(name="unload")
async def unload(ctx, extension):
    """unloads a cog"""
    client.unload_extension(f"cogs.{extension}")
    print("unloaded " + extension)
    await ctx.send("unloaded!")
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
async def dbdump(ctx):
    db = discord.File('chatbot.sqlite')
    try:
        await ctx.send(file=db, content="here is the chat db")
        print("db transferred")
    except:
        print("Error:Db not transferred")
    return None
#----------------------------------------#
@sudo.command(name="add_xp",aliases=["ax"])
async def add_xp(ctx, amount, user: discord.User):
    """Gives xp to a user"""
    User = user.id
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    cursor.execute(f"SELECT lvl, exp FROM level WHERE usr = '{User}'")
    res = cursor.fetchone()
    if res is not None:
        cursor.execute(f"UPDATE level SET exp=exp + {amount} WHERE usr = '{User}'")
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
        cursor.execute(f"INSERT INTO level VALUES({new_id}, '{User}', 1, {amount})")
        connection.commit()
        connection.close()
        await lvlup(ctx, User)
#--------------------------------------------------------------------------------#
def runner():    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
        else:
            pass
    client.run(configToken)
    logger 
    return None

if __name__ = '__main__':
    runner()
#------------------------------------------------------------------------------------------------------------------------#
