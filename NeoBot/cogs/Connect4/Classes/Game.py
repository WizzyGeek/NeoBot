"""A connect4 game using a board."""
from typing import List
from itertools import chain, groupby

import discord

from .Board import Board

class Connect4Game:
	__slots__ = frozenset({'board', 'turn_count', '_whomst_forfeited', 'names'})

	FORFEIT: int = -2
	TIE: int = -1
	NO_WINNER: int = 0

	PIECES: List[str] = (
		u"\u2B1B"
		u'\U0001f7e5'
		u'\U0001f7e6'
	)

	def __init__(self, x, y, player1_name=None, player2_name=None):
		if player1_name is not None and player2_name is not None:
			self.names: Tuple[str] = (player1_name, player2_name)
		else:
			self.names: Tuple[str] = ('Player 1', 'Player 2')

		self.board: Board = Board(x, y)
		self.turn_count: int = 0
		self._whomst_forfeited = ""

	def move(self, column: int) -> None:
		self.board[column] = self.whomst_turn()
		self.turn_count += 1

	def forfeit(self) -> None:
		"""forfeit the game as the current player"""
		self._whomst_forfeited = self.whomst_turn_name()

	def _get_forfeit_status(self) -> str:
		if self._whomst_forfeited:
			status = '{} won \nAs {} forfeited.\n'

			return status.format(
				self.other_player_name(),
				self.whomst_turn_name()
			)

		raise ValueError('Nobody has forfeited')

	def build_embed(self) -> discord.Embed:
		win_status = self.whomst_won()
		status: str = self._get_status()
		instructions: str = self._get_instructions()

		if win_status == self.FORFEIT:
			status = self._get_forfeit_status()

		empty = "\n"
		# self._format_row(y) for y in range(self.board.height)
		return discord.Embed(title=status, description=f"{empty.join(map(lambda y: self._format_row(y), range(self.board.height)))}{empty}{instructions}")

	def __str__(self) -> str:
		win_status: int = self.whomst_won()
		status = self._get_status()
		instructions = ''

		if win_status == self.NO_WINNER:
			instructions = self._get_instructions()
		elif win_status == self.FORFEIT:
			status = self._get_forfeit_status()

		return (
			status
			+ instructions
			+ '\n'.join(self._format_row(y) for y in range(self.board.height))
		)

	def _get_status(self) -> str:
		win_status: int = self.whomst_won()

		if win_status == self.NO_WINNER:
			status = (self.whomst_turn_name() + "'s turn | "
				+ self.PIECES[self.whomst_turn()])
		elif win_status == self.TIE:
			status = "It's a tie!"
		elif win_status == self.FORFEIT:
			status = self._get_forfeit_status()
		else:
			status = self._get_player_name(win_status) + ' won!'
		return status + '\n'

	def _get_instructions(self) -> str:
		instructions: str = ''
		for i in range(1, self.board.width+1):
			instructions += str(i) + '\N{combining enclosing keycap}'
		return instructions + '\n'

	def _format_row(self, y: int):
		return ''.join(self[x, y] for x in range(self.board.width))

	def __getitem__(self, pos) -> str:
		x, y = pos
		return self.PIECES[self.board[x, y]]

	def whomst_won(self) -> int:
		"""Get the winner on the current board.
		If there's no winner yet, return Connect4Game.NO_WINNER.
		If it's a tie, return Connect4Game.TIE"""

		lines = (
			self.board, # columns
			zip(*self.board), # rows (zip picks the nth item from each column)
			self.board._pos_diagonals(), # positive diagonals
			self.board._neg_diagonals(), # negative diagonals
		)

		if self._whomst_forfeited:
			return self.FORFEIT

		for line in chain(*lines):
			for player, group in groupby(line):
				if player != 0 and len(list(group)) >= 4:
					return player

		if self.board._full():
			return self.TIE

		return self.NO_WINNER

	def other_player_name(self) -> str:
		return self._get_player_name(self.whomst_turn() - 1)

	def whomst_turn_name(self) -> str:
		return self._get_player_name(self.whomst_turn())

	def whomst_turn(self) -> int:
		return self.turn_count%2+1

	def _get_player_name(self, player_number) -> str:
		player_number -= 1 # these lists are 0-indexed but the players aren't

		return self.names[player_number]
