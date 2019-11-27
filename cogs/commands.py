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
        await ctx.send(f"Answer: {random.choice(ans)}")

    @commands.command(name="graffiti", aliases=["art"])
    async def graffiti(self, ctx):
        await ctx.send("""

        ──────────────────▒
        ─────────────────░█
        ────────────────███
        ───────────────██ღ█
        ──────────────██ღ▒█──────▒█
        ─────────────██ღ░▒█───────██
        ─────────────█ღ░░ღ█──────█ღ▒█
        ────────────█▒ღ░▒ღ░█───██░ღღ█
        ───────────░█ღ▒░░▒ღ░████ღღღ█
        ───░───────█▒ღ▒░░░▒ღღღ░ღღღ██─────░█
        ───▓█─────░█ღ▒░░░░░░░▒░ღღ██─────▓█░
        ───██─────█▒ღ░░░░░░░░░░ღ█────▓▓██
        ───██────██ღ▒░░░░░░░░░ღ██─░██ღ▒█
        ──██ღ█──██ღ░▒░░░░░░░░░░ღ▓██▒ღღ█
        ──█ღღ▓██▓ღ░░░▒░░░░░░░░▒░ღღღ░░▓█
        ─██ღ▒▒ღღ░░ღღღღ░░▒░░░░ ღღღღ░░ღღღ██
        ─█ღ▒ღღ█████████ღღ▒░ღ██████████ღ▒█░
        ██ღღ▒████████████ღღ████████████░ღ█▒
        █░ღღ████████████████████████████ღღ█
        █▒ღ██████████████████████████████ღ█
        ██ღღ████████████████████████████ღ██
        ─██ღღ██████████████████████████ღ██
        ──░██ღღ██████████████████████ღღ██
        ────▓██ღ▒██████████████████▒ღ██
        ───░──░███ღ▒████████████▒ღ███
        ────░░───▒██ღღ████████▒ღ██
        ───────────▒██ღ██████ღ██
        ─────────────██ღ████ღ█
        ───────────────█ღ██ღ█
        ────────────────█ღღ█
        ────────────────█ღ█░
        ─────────────────██░
        """)

    @commands.command(name="aware")
    async def aware(self, ctx):
        embed = discord.Embed(title="Spreading awareness is important", description=f"many people are still unaware of the **consequences** of deforestation, to save them the least you can do is to educate people, have a look at #what-can-i-do", colour=discord.Color.dark_blue())
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(utility(client))
