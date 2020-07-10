"""The Cog For managing the bot."""
import ast
import asyncio
import importlib
import inspect
import io
import logging
import pathlib
import textwrap
import traceback
from typing import List
from contextlib import redirect_stdout

import discord
from discord.ext import commands

from NeoBot import Neo

logger = logging.getLogger(__name__)


class Sudo(commands.Cog):
    """Cog for maintaining and updating the bot."""

    def __init__(self, bot: Neo):
        """Season it with some salt."""
        self.bot: Neo = bot
        self.sessions = set()
        self._last_result = None
    #----------------------------------------#
    async def _load_extension(self, extension: str):
        cog_dir: pathlib.Path = self.bot.cog_dir
        if extension in self.bot.packaged_cogs:
            path = cog_dir / extension / "__init__.py"
        else:
            path = cog_dir / f"{extension}.py"
        try:
            if extension in self.bot._BotBase__extensions:
                return
            spec = importlib.util.spec_from_file_location(extension, path)
            if spec is not None:
                self.bot._load_from_module_spec(spec, extension)
            else:
                raise commands.ExtensionNotFound(extension)
        except Exception as err:
            logger.info(f"Failed to load Cog | ⚙ | {extension} at {path}", exc_info=True)
            raise err
        else:
            logger.info(f"Loaded Cog - | ⚙ | {extension} at {path}")
            return

    async def _reload_extension(self, extension: str):
        try:
            self.bot.unload_extension(extension)
        except Exception as err:
            logger.info(f"Failed to unload Cog | ⚙ | {extension}")
        else:
            logger.info(f"Unloaded Cog | ⚙ | {extension}")
        finally:
            await self._load_extension(extension)

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
            res = await self._load_extension(extension)
        except Exception as err:
            await ctx.send(embed=self.bot.Qembed(ctx, title="Failed", content=f"Failed to load {extension}", Colour=3).add_field(name="Error", value=err))
        else:
            await ctx.send(embed=self.bot.Qembed(ctx, title="Done", content=f"loaded {extension}", Colour=1))
    #----------------------------------------#

    @sudo.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *, extension: str) -> None:
        """Reload a cog."""
        if extension.lower() in ("all", "*"):
            extensions = [str(n) for n in self.bot._BotBase__extensions]
        else:
            extensions = extension.replace(" ", "").split(",")
        res: List[str] = []
        for ext in extensions:
            try:
                await self._reload_extension(ext)
            except Exception as err:
                res.append(f"`{ext}` | Failed | {err}")
            else:
                res.append(f"`{ext}` | Reloaded")
        else:
            await ctx.send(embed=self.bot.Qembed(ctx, title="Reloaded", content="\n".join([n for n in res])))
    #----------------------------------------#

    @sudo.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension: str) -> None:
        """Unload a cog."""
        try:
            self.bot.unload_extension(f"{extension}")
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
        embed = self.bot.Qembed(ctx, title="Extensions", content="\n".join([f"`{n}`" for n in self.bot._BotBase__extensions]))
        await ctx.send(embed=embed)
    #----------------------------------------#
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

    @commands.group(name="settings", aliases=["set", "setting"])
    @commands.is_owner()
    async def settings(self, ctx: commands.Context):
        pass

    @settings.command(name="name")
    @commands.is_owner()
    async def set_name(self, ctx: commands.Context, *, name: str):
        """Sets the bot's name."""
        name = name.strip()
        if name != "":
            await self.bot.user.edit(username=name)
        else:
            await self.bot.send_command_help(ctx)
    
    @settings.command(name="game")
    @commands.is_owner()
    @commands.guild_only()
    async def set_game(self, ctx: commands.Context, *, game: str = None):
        """Sets the bot's playing status
        Leaving this empty will clear it."""
        guild = ctx.message.guild

        current_status = guild.me.status if guild is not None else None

        if game:
            await self.bot.change_presence(activity=discord.Game(game), status=current_status)
            await ctx.send(f"Game set to {game}")
        else:
            await self.bot.change_presence(activity=None, status=current_status)
            await ctx.send('Cleared game status.')

    @settings.command(name="nick")
    @commands.is_owner()
    async def set_nickname(self, ctx: commands.Context, *, nickname: str = ""):
        """Sets the bot's nickname on the current server.
        Leaving this empty will remove it."""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await ctx.me.edit(nick=nickname)
            await ctx.send("Done.")
        except discord.Forbidden:
            await ctx.send("I cannot do that, I lack the \"Change Nickname\" permission.")

    @settings.command(name="status")
    @commands.is_owner()
    async def set_status(self, ctx: commands.Context, *, status: str = None):
        """Sets the bot's status
        Statuses:
            online
            idle
            dnd
            invisible"""
        guild = ctx.message.guild
        current_game = guild.me.game if guild is not None else None

        if status is None:
            await self.bot.change_presence(status=discord.Status.online, game=current_game)
            await ctx.send("Status reset.")
        else:
            await self.bot.change_presence(status=status, game=current_game)
            await ctx.send("Status set to {0}.".format(status))

    @settings.command(name="stream")
    @commands.is_owner()
    async def set_stream(self, ctx: commands.Context, streamer: str = None, *, stream_title: str = None):
        """Sets the bot's streaming status.
        Leaving both streamer and stream_title empty will clear it."""
        guild = ctx.message.guild

        current_status = guild.me.status if guild is not None else None

        if stream_title:
            stream_title = stream_title.strip()
            if "twitch.tv/" not in streamer:
                streamer = "https://www.twitch.tv/" + streamer
            stream = discord.Streaming(url=streamer, name=stream_title)
            await self.bot.change_presence(activity=stream, status=current_status)
        elif streamer is not None:
            await ctx.send("Specify a streamer!")
            return
        else:
            await self.bot.change_presence(activity=None, status=current_status)
        await ctx.send("Done | ✅")
 
    @settings.command(name="avatar")
    @commands.is_owner()
    async def set_avatar(self, ctx: commands.Context, url: str):
        """Sets the bot's avatar."""
        try:
            async with session.get(url) as img:
                image_data = await img.read()
            await self.bot.user.edit(avatar=image_data)
            await ctx.send("Done | ✅")
            self.log.debug("Changed avatar.")
        except discord.HTTPException as ex:
            await ctx.send("**Failed |** :negative_squared_cross_mark:")
            self.log.exception(ex)
            traceback.print_exc()

    @settings.command(name="description", aliases=["desc"])
    @commands.is_owner()
    async def set_description(self, ctx: commands.Context, *, description: str):
        """Sets the bot's description."""
        self.bot.description = inspect.cleandoc(description) if description else ''
        await ctx.send("**Done | ✅**\nSet the description.")

    # command not needed
    # @sudo.command(name="restart", aliases=['reboot'],description="restarts the entire bot")
    # @commands.is_owner()
    # async def reboot(self, ctx):
    #     logger.info(f"[IMP]Reboot request from {ctx.author.name} received.")
    #     await self.bot.logout()
    #     await self.bot.run()
    #     return None
    #--------------------------------------------------------------------------------#


def setup(bot: Neo) -> None:
    """Into pan goes the cog."""
    bot.add_cog(Sudo(bot))
