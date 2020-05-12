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
        await ctx.send("""```fix

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
        ```""")

"""
    @commands.command(name="aware")
    async def aware(self, ctx):
        embed = discord.Embed(title="Spreading awareness is important", description=f"many people are still unaware of the **consequences** of deforestation, to save them the least you can do is to educate people, have a look at #what-can-i-do", colour=discord.Color.dark_blue())
        await ctx.send(embed=embed)

    @commands.command(name="rainforest")
    async def rain(self, ctx):
        embed = discord.Embed(title="RainForest", description=f"A luxuriant, dense forest rich in biodiversity, We need the rain forests to produce oxygen and clean the atmosphere to help us breathe. We also know that the earth's climate can be affected, as well as the water cycle", colour=discord.Color.green())
        await ctx.send(embed=embed)
    
    @commands.command(name="debate")
    async def debate(self, ctx):
        embed = discord.Embed(title="The spirit of debate", description=f"Good debates require the participants to:\nBe fair-minded\nMake a good-faith attempt to persuade\nShow respect", colour=discord.Color.dark_blue())
        await ctx.send(embed=embed)

    @commands.command(name="climatechange")  
    async def climate(self, ctx):
        embed = discord.Embed(title="Climate Change: How Do We Know?", description=f"Just in the last 650,000 years there have been seven cycles of glacial advance and retreat, with the abrupt end of the last ice age about 11,700 years ago marking the beginning of the modern climate era — and of human civilization. Most of these climate changes are attributed to very small variations in Earth’s orbit that change the amount of solar energy our planet receives.", colour=discord.Color.dark_blue())
        embed.set_image(url="https://climate.nasa.gov/system/content_pages/main_images/203_co2-graph-061219.jpg")
        await ctx.send(embed=embed)

    @commands.command(name="10myths")
    async def myths(self, ctx):
        embed = discord.Embed(title="Top 10 Myths about the enviroment!", url="https://www.wwf.org.uk/updates/10-myths-about-climate-change", colour=discord.Color.dark_blue())
        await ctx.send(embed=embed)
"""

def setup(client):
    client.add_cog(utility(client))
