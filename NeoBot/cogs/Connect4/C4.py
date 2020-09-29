
import asyncio
import discord
from discord.ext import commands

import logging
from typing import List

from .Classes.Game import Connect4Game

logger = logging.getLogger(__name__)

class Connect4(commands.Cog):
    CANCEL_GAME_EMOJI: str = '🚫'
    GAME_TIMEOUT_THRESHOLD = 60

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="c4", aliases=["connect4", "con4"])
    async def c4(self, ctx, player2: discord.Member, x: int = 7, y: int = 6) -> None:
        """Play connect4 with another player"""
        if x > 9 or y > 9:
            return await ctx.send("Board can\'t be bigger than 9x9")
        if x <= 0 or y <= 0:
            return await ctx.send("Board's diemensions cant be zero or less")
        if player2.bot:
            return await ctx.send("You can\'t play with Bots!")
        if player2 == ctx.author:
            return await ctx.send("You can't play with yourself,\nThere is no fun in that.")

        DIGITS: List[str] = [str(digit) + '\N{combining enclosing keycap}' for digit in range(1, x + 1)]
        VALID_REACTIONS = DIGITS.append(self.CANCEL_GAME_EMOJI)

        player1: discord.Member = ctx.author

        game = Connect4Game(
            x,
            y,
            player1.display_name,
            player2.display_name,
        )

        message: discord.Message = await ctx.send(embed=game.build_embed())

        for digit in VALID_REACTIONS:
            await message.add_reaction(digit)

        def check(reaction, user) -> bool:
            return (
                user == (player1, player2)[game.whomst_turn()-1]
                and str(reaction) in VALID_REACTIONS
                and reaction.message.id == message.id
            )

        while game.whomst_won() == game.NO_WINNER:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check=check,
                    timeout=self.GAME_TIMEOUT_THRESHOLD
                )
            except asyncio.TimeoutError:
                game.forfeit()
                break

            await asyncio.sleep(0.1)
            try:
                await message.remove_reaction(reaction, user)
            except discord.errors.Forbidden:
                pass

            if str(reaction) == self.CANCEL_GAME_EMOJI:
                game.forfeit()
                break

            try:
                # convert the reaction to a 0-indexed int and move in that column
                game.move(self.DIGITS.index(str(reaction)))
            except ValueError:
                pass # the column may be full

            await message.edit(embed=game.build_embed())

        await self.end_game(game, message)
        return None

    async def end_game(self, game: Connect4Game, message: discord.Message) -> None:
        await message.edit(embed=game.build_embed())
        await self.clear_reactions(message)
        return None

    @staticmethod
    async def clear_reactions(message: discord.Message) -> None:
        try:
            await message.clear_reactions()
        except discord.HTTPException:
            logger.warning("Failed to clear exceptions", exc_info=True)
        return None
