import ast
import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
            
class Sudo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #----------------------------------------#
    @commands.group()
    @commands.has_permissions(administrator = True)
    async def sudo(self, ctx):
        logger.info(f"elevated privilage use detected, USER : {ctx.author.name}")
        return None
    #----------------------------------------#
    @sudo.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, extension):
        """loads a cog"""
        # To Test if .pysc can be loaded
        self.bot.load_extension(f"cogs.{extension}") 
        logger.info(f"Loaded Cog {extension}")
        await ctx.send(embed=discord.Embed(title="Done",description=f"loaded {extension}"))
    #----------------------------------------#
    @sudo.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, *, extension):
        """reloads a cog"""
        self.bot.unload_extension(f"cogs.{extension}")
        self.bot.load_extension(f"cogs.{extension}")
        logger.info(f"Reloaded Cog {extension}")
        await ctx.send(embed=discord.Embed(title="Done",description=f"Reloaded {extension}"))
    #----------------------------------------#
    @sudo.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """unloads a cog"""
        self.bot.unload_extension(f"cogs.{extension}")
        logger.info(f"unloaded Cog {extension}")
        await ctx.send(embed=discord.Embed(title="Done",description=f"unloaded {extension}", colour = 0x00eb04))
    #----------------------------------------#
    @sudo.command(name="eval")
    async def eval_fn(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
          - `bot`: the bot instance
          - `discord`: the discord module
          - `commands`: the discord.ext.commands module
          - `ctx`: the invokation context
          - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        await ctx.send(result)
    #----------------------------------------#
    # command not needed
    # @sudo.command(name="restart", aliases=['reboot'],description="restarts the entire bot")
    # @commands.is_owner()
    # async def reboot(self, ctx):
    #     logger.info(f"[IMP]Reboot request from {ctx.author.name} received.")
    #     await self.bot.logout()
    #     await self.bot.run()
    #     return None
    #--------------------------------------------------------------------------------#
def setup(bot):
    bot.add_cog(Sudo(bot))