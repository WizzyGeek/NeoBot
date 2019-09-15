#ai
import re
import sqlite3
from collections import Counter
from string import punctuation
from math import sqrt
import discord
from discord.ext import commands
import asyncio

client = commands.Bot(command_prefix="$")

class ai(commands.Cog):
    def __init__(self, client):
        self.client = client

    @client.event
    async def on_message(self, message):
        pass

    @commands.command(aliases=['c','ch','cha','4'])
    async def chat(self, ctx, *, inp):
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

        def check(author):
            def inner_check(message):
                return message.content
            return inner_check

        Bot = 'Hello!'
        while True:
            await ctx.send('Bot: ' + Bot)

            try:
                msg = await client.wait_for('message', check=check(ctx.author))                
            except asyncio.TimeoutError:
                await ctx.send('Bot: bye')
                break
            mid_you = msg.content
            you = mid_you.strip()
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
                cursor.execute('SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
                row = cursor.fetchone()
            
            Bot = row[1]
            cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))            

def setup(client):
    client.add_cog(ai(client))
