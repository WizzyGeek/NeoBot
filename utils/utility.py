import sqlite3
import asyncio
import tracemalloc
import traceback
tracemalloc.start()
#1
async def ErrorHandler(err, connection):
    """Handles all sql errors must. function is a coro.Needs an open connection."""
    connection.commit()
    connection.close()
    with open("errors.log", "a") as logfile:
        traceback.print_exc(file=logfile)
    print("an Error was caught")
    return None
#----------------------------------------#
async def rank_query(user):
    ##print(user)
    connection = sqlite3.connect("level.db")
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
    connection = sqlite3.connect("level.db")
    cursor = connection.cursor()
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
            return users
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