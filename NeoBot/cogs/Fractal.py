import asyncio
import concurrent.futures
import inspect
import os
import pathlib
from collections import OrderedDict

import discord
from discord.ext import commands, tasks

from fractal import Point, exec_command

Point.__str__ = lambda self: "x".join(map(str, self))


def basic_str(el): return str(el).lstrip(
    "(").rstrip(")")  # Complex or model name


def item_str(k, v): return (basic_str(v) if k in ["model", "c"] else
                            "{}={}".format(k, v))


def filename(kwargs): return "-".join(item_str(*pair)
                                      for pair in kwargs.items())


def comp(x, y):
    """return a complx no."""
    if y > 0:
        return complex(f"{x}+{y}j")
    else:
        return complex(f"{x}{y}j")

class Fractal(commands.Cog):
    """generate Fractals and send them on discord"""

    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

    async def send_frac(self, ctx, Model):
        """send a Model"""
        name = f"{filename(Model)}.png"
        Model["output"] = pathlib.Path(__file__).parent.absolute() / "img" / name

        if Model["output"].is_file():
            pass
        else:
            fractal = self.loop.run_in_executor(self.executor, lambda: exec_command(Model))
            await asyncio.gather(fractal)

        embed = self.bot.Qembed(ctx, title="Stats for nerds", content="\n".join([str(stat) for stat in Model.items() if stat[0] != "output"]))
        return await ctx.send(embed=embed, file=discord.File(Model["output"]))

    @commands.group(name="fractal", no_pm=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def fractal(self, ctx):
        """Top-level fractal command"""
        pass

    @fractal.command(name="mandelbrot")
    async def mandelbrot(self, ctx, sizeX: int = 500, sizeY: int = 300, depth: int = 100, zoom: float = 1.2, centerX: float = -1.5, centerY: float = 0):
        """Generate a mandelbrot model and send it"""
        if sizeX > 800 or sizeY > 800 or depth > 512:
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Argument too big!", content="Max first 3 args are \n `fractal julia 800 800 512`"))
        else:
            Model = {
                "model": "mandelbrot",
                "size": Point(sizeX, sizeY),
                "depth": depth,
                "zoom": zoom,
                "center": Point(centerX, centerY),
                "show": False
            }
            async with ctx.typing():
                await self.send_frac(ctx, Model)

    @fractal.command(name="julia")
    async def julia(self, ctx, sizeX: int = 500, sizeY: int = 300, depth: int = 100, zoom: float = 1.2, centerX: float = -0.456, centerY: float = 0.67):
        """Generate a julia model and send it"""
        if sizeX > 800 or sizeY > 800 or depth > 512:
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Argument too big!", content="Max first 3 args are \n `fractal mandelbrot 800 800 512`"))
        else:
            Model = {
                "model": "julia",
                "size": Point(int(sizeX), int(sizeY)),
                "depth": int(depth),
                "zoom": float(zoom),
                "c": comp(centerX, centerY),
                "show": False
            }

            async with ctx.typing():
                await self.send_frac(ctx, Model)

    @fractal.error
    async def fractal_error(self, ctx, error):
        """Cooldown handler"""
        if isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(
                embed=self.bot.Qembed(ctx, title="Slow Down!",
                                      content=f"""Generating fractals requires lot of 
                                            computation power hence to prevent abuse,
                                            this command has a 30 second cooldown in the 
                                            entire server. try again in `{error.retry_after} seconds`"""))

    @tasks.loop(hours=36)
    async def storage_optimizer(self):
        """reset fractal cache every 1.5 days"""
        path = pathlib.Path(__file__).parent.absolute() / "img"
        files = os.listdir(path)
        if len(files) > 2:
            file_names = [f for f in files if os.path.isfile(
                os.path.join(path, f))]
            png_file_names = [f for f in file_names if f.endswith(".png") and f not in [
                "mandelbrot-size=500x300-depth=100-zoom=1.2-center=-1.5x0-show=False.png", "julia-size=500x300-depth=100-zoom=1.2--0.456+0.67j-show=False.png"]]
            for file in png_file_names:
                os.remove(file)
        else:
            pass


def setup(bot):
    bot.add_cog(Fractal(bot))
