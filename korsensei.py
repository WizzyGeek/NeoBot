import os
import re
import sqlite3
from collections import Counter
from string import punctuation
from math import sqrt
import discord
from discord.ext import commands
import asyncio
import random
#----------------------------------------#
client = commands.Bot(command_prefix="$")
guild = discord.Guild
user = discord.Client()
#----------------------------------------#
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name='my students', type=discord.ActivityType.watching, status=discord.Status.idle))
    print('We have logged in as {0.user}'.format(client))
 
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')
    channel = client.get_channel(583703372725747713)
    await channel.send("welcome to the gang {member.mention}")

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    print("loaded " + extension)
    await ctx.send("loaded!")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    print("reloaded " + extension)
    await ctx.send("reloaded!")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    print("unloaded " + extension)
    await ctx.send("unloaded!")


@client.command(aliases=['c','ch'])
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
        wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
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
            print("ERROR: NO INPUT PROVIDED!")

        print(you)

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
            cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))

        connection.commit()

        cursor.execute('CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
        words = get_words(you)
        words_length = sum([n * len(word) for word, n in words])

        for word, n in words:
            weight = sqrt(n / float(words_length))
            cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))

        cursor.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
        row = cursor.fetchone()
        cursor.execute('DROP TABLE results')

        if row is None:
            cursor.execute(
                'SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
            row = cursor.fetchone()

        Bot = row[1]
        cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))
        print('Bot: ' + Bot)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
    else:
        pass

client.run('NjE5ODk2OTcyMTUyOTMwMzA4.Xc0eRw.OBUWRWobEvWmERpgGckJf_M3OcI')
