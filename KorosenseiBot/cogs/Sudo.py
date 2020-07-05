"""The Cog For managing the bot."""
import ast
import asyncio
import logging
import io
import inspect
from contextlib import redirect_stdout
import traceback
import textwrap

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class Sudo(commands.Cog):
    """Cog for maintaining and updating the bot."""
    
    def __init__(self, bot):
        """Season it with some salt."""
        self.bot = bot
        self.sessions = set()
        self._last_result = None
    #----------------------------------------#

    @commands.group()
    @commands.has_permissions(administrator=True) # REASON : [If you are admin in that server then you may
    async def sudo(self, ctx: commands.Context) -> None:    # use owner commands there since you may try to
        """Log what they do."""                             # exploit this cog in any server]
        logger.info(
            f"elevated privilage use detected, USER : {ctx.author.name}")
        return None
    #----------------------------------------#

    @sudo.command(name="load")
    @commands.is_owner()
    async def load(self, ctx: commands.Context, extension: str) -> None:
        """Load a cog."""
        # To Test if .pysc can be loaded
        try:
            self.bot.load_extension(f"cogs.{extension}")
        except Exception as err:
            logger.exception("Extension load failed")
            await ctx.send(embed=self.bot.Qembed(ctx, title="Failed", content=f"Failed to load {extension}", Colour=3).add_field(name="Error", value=err))
        else:
            logger.info(f"Loaded Cog {extension}")
            await ctx.send(embed=self.bot.Qembed(ctx, title="Done", content=f"loaded {extension}", Colour=1))
    #----------------------------------------#

    @sudo.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension: str) -> None:
        """Reload a cog."""
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except Exception as err:
            logger.exception("Extension reload failed")
            await ctx.send(embed=self.bot.Qembed(ctx, title="Failed", content=f"Failed to reload {extension}", Colour=3).add_field(name="Error", value=err))
        else:
            logger.info(f"Loaded Cog {extension}")
            await ctx.send(embed=self.bot.Qembed(ctx, title="Done", content=f"reloaded {extension}", Colour=1))
    #----------------------------------------#

    @sudo.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension: str) -> None:
        """Unload a cog."""
        try:
            self.bot.unload_extension(f"cogs.{extension}")
        except Exception as err:
            logger.exception("Extension unload failed")
            await ctx.send(embed=self.bot.Qembed(ctx, title="Failed", content=f"Failed to unload {extension}", Colour=3).add_field(name="Error", value=err))
        else:
            logger.info(f"Loaded Cog {extension}")
            await ctx.send(embed=self.bot.Qembed(ctx, title="Done", content=f"unloaded {extension}", Colour=1))
    #----------------------------------------#
    @commands.is_owner()
    @commands.command()
    async def extensions(self, ctx: commands.Context):
        """All active bot extensions."""
        embed = self.bot.Qembed(ctx, title="Extensions", content="\n".join([f"`{n.split('.')[1]}`" for n in self.bot._BotBase__extensions]))
        await ctx.send(embed=embed)
    """Sourced From RoboDanny"""

    def get_syntax_error(self, e: Exception):
        """Capture the text from an error."""
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'
    #----------------------------------------#

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')
    #----------------------------------------#

    @sudo.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launch an interactive REPL session."""
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

            if cleaned in ('quit', 'exit', 'exit()', 'quit()'):
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
    #----------------------------------------#
    @sudo.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluate a code."""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    # command not needed
    # @sudo.command(name="restart", aliases=['reboot'],description="restarts the entire bot")
    # @commands.is_owner()
    # async def reboot(self, ctx):
    #     logger.info(f"[IMP]Reboot request from {ctx.author.name} received.")
    #     await self.bot.logout()
    #     await self.bot.run()
    #     return None
    #--------------------------------------------------------------------------------#


def setup(bot: commands.Bot) -> None:
    """Into pan goes the cog."""
    bot.add_cog(Sudo(bot))
