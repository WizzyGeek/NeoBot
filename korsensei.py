
import discord
from discord.ext import commands
client = discord.Client()
bot = commands.Bot(command_prefix='$')

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
            if message.content.startswith('$hello'):
                await message.channel.send(ok)
            else:
                pass
        else:
            pass
    else:
        pass


@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)


@bot.command()
async def multiply(ctx, a: int, b: int):
    await ctx.send(a*b)


@bot.command()
async def greet(ctx):
    await ctx.send(":smiley: :wave: Hello, there!")


@bot.command()
async def cat(ctx):
    await ctx.send("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif")


@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="nice bot", description="Nicest bot there is ever.", color=0xeee657)

    # give info about you here
    embed.add_field(name="Author", value="<YOUR-USERNAME>")

    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    # give users a link to invite thsi bot to their server
    embed.add_field(
        name="Invite", value="[Invite link](<insert your OAuth invitation link here>)")

    await ctx.send(embed=embed)

bot.remove_command('help')


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="nice bot", description="A Very Nice bot. List of commands are:", color=0xeee657)

    embed.add_field(
        name="$add X Y", value="Gives the addition of **X** and **Y**", inline=False)
    embed.add_field(name="$multiply X Y",
                    value="Gives the multiplication of **X** and **Y**", inline=False)
    embed.add_field(
        name="$greet", value="Gives a nice greet message", inline=False)
    embed.add_field(
        name="$cat", value="Gives a cute cat gif to lighten up the mood.", inline=False)
    embed.add_field(
        name="$info", value="Gives a little info about the bot", inline=False)
    embed.add_field(name="$help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)

bot.run('NDE0MzIyMDQ1MzA0OTYzMDcy.DWl2qw.nTxSDf9wIcf42te4uSCMuk2VDa0')

client.run('NjE5ODk2OTcyMTUyOTMwMzA4.XXPKfw.YWBRFpfDcQcfwbtlBTZw5L9d2_I')
