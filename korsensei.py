import discord
from discord.ext import commands
bot = commands.Bot(command_prefix='$')
client = discord.Client()
embed = discord.Embed()

@client.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@client.event
async def on_message(message):
    await client.process_message()

@bot.command
async def cool(ctx):
    ctx.send("thx")


client.run('NjE5ODk2OTcyMTUyOTMwMzA4.XXYVVA.4-SIlkPjobYpLOWkGxhE6XeDqyI')
#jE5ODk2OTcyMTUyOTMwMzA4.XXYVVA.4N-SIlkPjobYpLOWkGxhE6XeDqyI
