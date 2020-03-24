import asyncio
import logging
import os
import sqlite3
import sys
import traceback
import tracemalloc

import discord
import psycopg2

logger = logging.getLogger(__name__)
DATABASE_URL = os.environ['DATABASE_URL']
tracemalloc.start()
#1
async def ErrorHandler(err, connection):
    """Handles all sql errors must. function is a coro.Needs an open connection."""
    connection.commit()
    connection.close()
    return None
#----------------------------------------#
async def rank_query(user):
    ##print(user)
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT user FROM level ORDER BY exp DESC")
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
async def ranking(range):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()
    def substitute(users):
        client = discord.Client()
        for userid in users:
            name = client.get_user(userid)
            userid = name
        return users
    try:
        cursor.execute("SELECT user FROM level ORDER BY exp DESC")
        res = cursor.fetchall()
    except Exception as err:
        ErrorHandler(err, connection)
    users = []
    count = 1
    for element in res:
        if element is not None:
            users.append(element)
            count += 1
        elif count == range or element is None:
            substitute(users)
            return users
    substitute(users)
    return users
#----------------------------------------#
async def AppendToTuple(data, value):
    Array = []
    for element in data:
        Array.append(element)
    Array.append(value)
    print(Array)
    return Array
#----------------------------------------#
async def LevelsQuery(user):#important!!!!
    connection = sqlite3.connect("level.db")
    cursor = connection.cursor()
    Rank = await rank_query(user)
    print(Rank)
    try:
        cursor.execute(f"SELECT exp, lvl FROM level WHERE user = '{user}'")
        res = cursor.fetchone()
        if res == None:
            return None
        else:
            pass
        Array = await AppendToTuple(res, Rank)
        connection.commit()
        connection.close()
        return Array
    except Exception as err:
        await ErrorHandler(err, connection)
        return None
#----------------------------------------#
async def RankUserQuery(rank):
    connection = sqlite3.connect("level.db")
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT user FROM level ORDER BY exp DESC")
        res = cursor.fetchall()
    except Exception as err:
        ErrorHandler(err, connection)
    count = 1
    for element in res:
        if element is not None and rank == count:
            return element
        else:
            count += 1
#----------------------------------------#
async def update(message):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()

    try:
        cursor.execute("SAVEPOINT my_save_point")
        cursor.execute("CREATE TABLE level(id INTEGER NOT NULL UNIQUE, usr BIGINT NOT NUll UNIQUE, lvl INTEGER NOT NULL, exp INTEGER);")
    except psycopg2.errors.DuplicateTable:
        cursor.execute("rollback to savepoint my_save_point")
    finally:
        cursor.execute("release savepoint my_save_point")
        connection.commit()

    weight = (round(len(str(message.content))**1/2))/2
    if weight > 15:
        weight = 15
    cursor.execute(f"SELECT usr FROM level WHERE usr = '{message.author.id}'")
    res = cursor.fetchone()
    try:
        if res is not None:
            cursor.execute(f"UPDATE level SET exp=exp + {weight} WHERE usr = '{message.author.id}'")
            connection.commit()
            logger.info(f"Author:{message.author},msg:{message.content},XP:{weight}")
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
            logger.info(f"New Entry : Author:{message.author},msg:{message.content},XP:{weight}")
            connection.commit()
            connection.close()
            await lvlup(message, message.author.id)
            return
    except psycopg2.errors.InFailedSqlTransaction as err:
        await ErrorHandler(err, connection)
        logger.critical(f"FATAL ERROR OCCURED!! Leveling system crash detected. \n ID:{id},XP:{weight}}", exc_info = True)
    return None

#----------------------------------------#
async def lvlup(ctx, id):
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')

        cursor = connection.cursor()
        cursor.execute(f"SELECT lvl, exp FROM level WHERE usr = '{id}'")
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
            embed = discord.Embed(title=f"{discord.Client().get_user(id)} just leveled up", description=f":tada:You now have **{exp}XP** and your level is **{lvl_end}**! Keep going! your rank is **{rank}**", colour=discord.Color.dark_blue())
            await ctx.channel.send(content=None, embed=embed)
            cursor.execute(f"UPDATE level SET lvl = {lvl_end} WHERE usr = '{id}'")
            connection.commit()
            connection.close()
    except psycopg2.errors.InFailedSqlTransaction as err:
        await ErrorHandler(err, connection)
        logger.critical(f"FATAL ERROR OCCURED, Leveling system crash detected. \n ID:{id},lvl:{lvl_end}", exc_info = True)
    return None
