import discord
from discord.ext import commands
import random
client = commands.Bot(command_prefix="$")


class utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ping", aliases=["latency", "lag"])
    async def ping(self, ctx):
        await ctx.send('Pong! {0}'.format(client.latency))

    @commands.command(aliases=['8ball', '8b', "luckyball"])
    async def _bball(self, ctx, *, question):
        ans = ['● It is certain.',
            '● It is decidedly so.',
            '● Without a doubt.',
            '● Yes - definitely.',
            '● You may rely on it.',
            '● As I see it, yes.',
            '● Most likely.',
            '● Outlook good.',
            '● Yes.',
            '● Signs point to yes.',
            '● Reply hazy, try again.',
            '● Ask again later.',
            '● Better not tell you now.',
            '● Cannot predict now.',
            '● Concentrate and ask again.',
            '● Don\'t count on it.',
            '● My reply is no.',
            '● My sources say no.',
            '● Outlook not so good.',
            '● Very doubtful.',
            ]
        await ctx.send(f"{random.choice(ans)}")

def setup(client):
    client.add_cog(utility(client))
