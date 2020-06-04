"""
import asyncio
import logging
import os
import sqlite3
import sys
import traceback
from math import floor

import discord
import psycopg2

logger = logging.getLogger(__name__)


#os.environ['DATABASE_URL'] = r"postgres://ovspnqbhsmynra:c5e500bb4fe1263ac459911d6461c02683a53ddb2467be4d48f040d7780eb041@ec2-54-197-34-207.compute-1.amazonaws.com:5432/d58tqf1iup8t6e"
try:
    #DATABASE_URL = os.environ['DATABASE_URL']
except Exception as err:
    logger.exception("Config vars inaccessible!")
    logger.warning("If datbase is URL not found leveling system will crash!")

#1
async def ErrorHandler(err, connection):
    Handles all sql errors must. function is a coro.Needs an open connection.
    connection.commit()
    connection.close()
    return None
#----------------------------------------#
async def rank_query(user):
    ##print(user)
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT ROW_NUMBER () OVER (ORDER BY xp) FROM level WHERE usr = {user};")
        res = cursor.fetchall()
    except Exception as err:
        ErrorHandler(err, connection)
    count = 1
    for re in res:
        for r in re:
            if r == str(user):
                connection.commit()
                connection.close()
                ##print(count)
                return count
            else:
                count += 1

#----------------------------------------#
async def IdPing(Id : int):
    ping = f"<@{str(Id)}>"
    return ping
#----------------------------------------#
async def ranking(range):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    #------------------------------------#
    try:
        cursor.execute(f"SELECT DISTINCT * FROM level ORDER BY xp DESC FETCH FIRST {range} ROWS ONLY;")
        res = cursor.fetchall()
    except Exception as err:
        await ErrorHandler(err, connection)
        logger.error("Transcation failed", exc_info = True)
    users = []
    for element in res:
        user = await IdPing(element[1])
        logger.info(user)
        users.append(user)
    return users


#----------------------------------------#
async def AppendToTuple(data, value):
    Array = []
    for element in data:
        Array.append(element)
    Array.append(value)
    return Array
#----------------------------------------#

async def LevelsQuery(user):#important!!!!-
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    Rank = await rank_query(user)
    try:
        cursor.execute(f"SELECT xp, lvl, ROW_NUMBER() OVER (ORDER BY xp) FROM level WHERE usr = {user};")
        res = cursor.fetchall()
        if res == None:
            return None
        else:
            pass
        connection.commit()
        connection.close()
        return res
    except Exception as err:
        await ErrorHandler(err, connection)
        logger.error("Transaction fail", exc_info=True)
        return Exception

#----------------------------------------#

async def RankUserQuery(rank):
    connection = sqlite3.connect("level.db")
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT user, xp, ROW_NUMBER () OVER (ORDER BY xp) FROM level WHERE ROW_NUMBER = {rank};")
        res = cursor.fetchone()
    except Exception as err:
        ErrorHandler(err, connection)
        logger.error("Transaction Failed", exc_info = True)
        return None 
    return res

#----------------------------------------#

async def update(message):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()

    try:
        cursor.execute("SAVEPOINT my_save_point;")
        cursor.execute("CREATE TABLE level(id INTEGER NOT NULL UNIQUE, usr BIGINT NOT NUll UNIQUE, lvl INTEGER NOT NULL, xp INTEGER);")
    except psycopg2.errors.DuplicateTable:
        cursor.execute("rollback to savepoint my_save_point;")
    finally:
        cursor.execute("release savepoint my_save_point;")
        connection.commit()

    weight = (round(len(str(message.content))**1/2))/2
    if weight > 15:
        weight = 15
    cursor.execute(f"SELECT usr FROM level WHERE usr = {message.author.id};")
    res = cursor.fetchone()
    try:
        if res is not None:
            cursor.execute(f"UPDATE level SET xp=xp + {weight} WHERE usr = {message.author.id};")
            connection.commit()
            logger.info(f"Author:{message.author},msg:{message.content},xp:{weight}")
            await lvlup(message, message.author.id)
            connection.close()
            return
        else:
            logger.info("New user found, adding to database")
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
            cursor.execute(f"INSERT INTO level VALUES({new_id}, '{message.author.id}', 1, {weight})")
            logger.info(f"New Entry : Author:{message.author},msg:{message.content},xp:{weight}")
            connection.commit()
            connection.close()
            await lvlup(message, message.author.id)
            return
    except psycopg2.errors.InFailedSqlTransaction as err:
        await ErrorHandler(err, connection)
        logger.critical(f"FATAL ERROR OCCURED!! Leveling system crash detected. \n ID:{id},xp:{weight}", exc_info = True)
    return None

#----------------------------------------#

async def lvlup(ctx, id):
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')

        cursor = connection.cursor()
        cursor.execute(f"SELECT lvl, xp FROM level WHERE usr = '{id}'")
        res = cursor.fetchone()
        if res == None:
            return None
        lvl = int(res[0])
        exp = int(res[1])
        msg = floor(exp/15)
        lvl_end = floor((msg ** 1/2)/6)
        if lvl < lvl_end:
            logger.info(f"LEVEL_UP : USERID:{client.get_user(id)}-lvl:{lvl_end}")
            rank = await rank_query(id)
            embed = discord.Embed(title=f"{discord.Client().get_user(id)} just leveled up", description=f":tada:You now have **{exp}xp** and your level is **{lvl_end}**! Keep going! your rank is **{rank}**", colour=discord.Color.dark_blue())
            await ctx.channel.send(content=None, embed=embed)
            cursor.execute(f"UPDATE level SET lvl = {lvl_end} WHERE usr = '{id}'")
            connection.commit()
            connection.close()
    except psycopg2.errors.InFailedSqlTransaction as err:
        await ErrorHandler(err, connection)
        logger.critical(f"FATAL ERROR OCCURED, Leveling system crash detected. \n ID:{id},lvl:{lvl_end}", exc_info = True)
    return None
"""
