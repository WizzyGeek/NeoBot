#------------imports------------#
import ast
import asyncio
import os
import random
import re
import sqlite3
from collections import Counter
from math import floor, sqrt
from string import punctuation
#-----------3rd-party-imports-----------#
import discord
from discord.ext import commands
#-----------module-imports-----------# 
from utils.utility import ErrorHandler, rank_query

#----------------------------------------#
client = commands.Bot(command_prefix="$")
guild = discord.Guild
user = discord.Client()
config = {
    "welchannel": 583703372725747713,
    "token": 'NjE5ODk2OTcyMTUyOTMwMzA4.Xc0eRw.OBUWRWobEvWmERpgGckJf_M3OcI',
    "embedcol": discord.Color.dark_blue()
}
#----------------------------------------#
@client.event
async def on_message(message):
    if message.author.bot:
        return
    elif isinstance(message.channel, discord.abc.PrivateChannel):
        return
    else:
        await update(message=message)

    await client.process_commands(message)

    return
#----------------------------------------#
async def update(message):
    connection = sqlite3.connect("level.db")
    cursor = connection.cursor()

    try:
        cursor.execute(
            "CREATE TABLE level(id INT NOT NULL UNIQUE, user TEXT UNIQUE, lvl INT NOT NULL, exp INT)")
        cursor.execute(
            "CREATE TABLE rank(user TEXT UNIQUE, rank INT NOT NULL)")
    except sqlite3.OperationalError:
        #await ErrorHandler(err, connection)
        pass

    weight = round(len(str(message))**1/2)
    if weight > 30:
        weight = 30
    cursor.execute(f"SELECT user FROM level WHERE user = '{message.author}'")
    res = cursor.fetchone()
    if res is not None:
        cursor.execute(
            f"UPDATE level SET exp=exp + {weight} WHERE user = '{message.author}'")
        connection.commit()
        await lvlup(message)
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
        cursor.execute(
            f"INSERT INTO level VALUES({new_id}, '{message.author}', 1, {weight})")
        connection.commit()
        connection.close()
        await lvlup(message)
        return
#----------------------------------------#
async def lvlup(message):
    try:
        connection = sqlite3.connect("level.db")
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT lvl, exp FROM level WHERE user = '{message.author}'")
        res = cursor.fetchone()
        if res == None:
            return None
        lvl = int(res[0])
        exp = int(res[1])
        msg = floor(exp/8)
        lvl_end = floor((msg ** 1/2)/5)
        if lvl < lvl_end:
            rank = await rank_query(message.author)
            embed = discord.Embed(title=f"{message.author} just leveled up", description=f":tada:you now have {exp}XP and your level is {lvl_end} !keep goin!!! you rank is {rank}", colour=config["embedcol"])
            await message.channel.send(content=None, embed=embed)
            cursor.execute(
                f"UPDATE level SET lvl = {lvl_end} WHERE user = '{message.author}'")
            connection.commit()
            connection.close()
    except sqlite3.OperationalError as err:
        await ErrorHandler(err, connection)
    return
#----------------------------------------#
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name='My Forests', type=discord.ActivityType.watching, status=discord.Status.idle))
    print('We have logged in as {0.user}'.format(client))
#----------------------------------------#
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')
    channel = client.get_channel(config["welchannel"])
    await channel.send(f"welcome to the gang {member.mention}")
#----------------------------------------#
""" @client.command(aliases=['c', 'ch'])
async def chat(ctx):
    connection = sqlite3.connect('chatbot.sqlite')
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

    """ def nobotspeakshere(message):
        if message.author.bot == False:
            return False
        elif message.author.bot == None:
            return True
    """
    Bot = 'Hello!'
    while True:
        you = ctx.message.content.strip()

        if you is None:
            await ctx.send("umm")

        if you == '':
            break
        elif you == 'bye':
            await ctx.send("Bot: bye")
            break
        else:
            pass

        words = get_words(Bot)
        words_length = sum([n * len(word) for word, n in words])
        sentence_id = get_id('sentence', you)

        for word, n in words:
            word_id = get_id('word', word)
            weight = sqrt(n / float(words_length))
            cursor.execute('INSERT INTO associations VALUES (?, ?, ?)',
                           (word_id, sentence_id, weight))

        connection.commit()

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
        await ctx.send('Bot: ' + Bot) """
#----------------------------------------#
@client.group()
@commands.is_owner()
async def sudo(ctx):
    auth = []
    if await ctx.bot.is_owner(ctx.author):
        pass
    elif ctx.author.id in auth:
        pass
    else:
        await ctx.send("you are not authorised")
        return Exception("user is bad")
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
@sudo.command(name="eval")
async def evalus(ctx, *, expr):
    """evaluates a pythonic expression"""
    str(expr)
    expr.replace("```", "")
    try:
        await ctx.send(eval(expr))SELECT
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
    db = discord.File('level.db')
    try:
        await ctx.send(file = db ,content = "here are the levels")
        print("db transferred")
    except:
        print("Error:Db not transferred")
#--------------------------------------------------------------------------------#
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
    else:
        pass
#----------------------------------------#
client.run(config["token"])
#------------------------------------------------------------------------------------------------------------------------#
