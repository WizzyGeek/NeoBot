import os
import discord
from discord.ext import commands
import random
#----------------------------------------#
client = commands.Bot(command_prefix="$")
guild = discord.Guild
#--------------------7--------------------#
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
    await ctx.send("loaded!")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.send("reloaded!")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send("unloaded!")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
    else:
        pass

client.run('token')
