import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    id = client.get_guild(583689248117489675)
    chs = ["bot-commands"]
    if message.author == client.user:
        return
    if str(message.channel) in chs:
        if message.content.startswith('$user'):
            await message.channel.send(f"no. of users is {id.member_count}")
        elif message.content.startswith('$invite'):
            await message.channel.send('https://discord.gg/MzsVHT3')
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

client.run('NjE5ODk2OTcyMTUyOTMwMzA4.XXPKfw.YWBRFpfDcQcfwbtlBTZw5L9d2_I')
