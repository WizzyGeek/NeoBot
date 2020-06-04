import ast
import asyncio
import logging
import io
import inspect
from contextlib import redirect_stdout
import traceback

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
        self.sessions = set()
    #----------------------------------------#

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def sudo(self, ctx):
        logger.info(
            f"elevated privilage use detected, USER : {ctx.author.name}")
        return None
    #----------------------------------------#

    @sudo.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, extension):
        """loads a cog"""
        # To Test if .pysc can be loaded
        self.bot.load_extension(f"cogs.{extension}")
        logger.info(f"Loaded Cog {extension}")
        await ctx.send(embed=discord.Embed(title="Done", description=f"loaded {extension}"))
    #----------------------------------------#

    @sudo.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, *, extension):
        """reloads a cog"""
        self.bot.unload_extension(f"cogs.{extension}")
        self.bot.load_extension(f"cogs.{extension}")
        logger.info(f"Reloaded Cog {extension}")
        await ctx.send(embed=discord.Embed(title="Done", description=f"Reloaded {extension}"))
    #----------------------------------------#

    @sudo.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """unloads a cog"""
        self.bot.unload_extension(f"cogs.{extension}")
        logger.info(f"unloaded Cog {extension}")
        await ctx.send(embed=discord.Embed(title="Done", description=f"unloaded {extension}", colour=0x00eb04))
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
    """Sourced From RoboDanny"""
    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')

        def check(m):
            return m.author.id == ctx.author.id and \
                   m.channel.id == ctx.channel.id and \
                   m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f'Unexpected error: `{e}`')
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
