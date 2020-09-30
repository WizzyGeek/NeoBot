"""2D Array emulating a Board."""

from typing import Union, Tuple

class Board(list):
	__slots__ = frozenset({'width', 'height'})

	def __init__(self, width: int, height: int):
		self.width: int = width
		self.height: int = height
		# 2D array of Zeroes
		for _ in range(width):
			self.append([0] * height)

	def __getitem__(self, pos: Union[int, Tuple[int]]):
		if isinstance(pos, int):
			return list(self)[pos]
		elif isinstance(pos, tuple):
			x, y = pos
			return list(self)[x][y]
		else:
			raise TypeError('pos must be an int or tuple')

	def __setitem__(self, pos: Union[int, Tuple[int]], new_value):
		x, y = self._xy(pos)

		if self[x, y] != 0:
			raise IndexError("position already defined.")

		# basically self[x][y] = new_value
		# super().__getitem__(x).__setitem__(y, new_value)
		self[x][y] = new_value

	def _xy(self, pos: Union[int, Tuple[int]]) -> Tuple[int]:
		if isinstance(pos, tuple):
			return pos[0], pos[1]
		elif isinstance(pos, int):
			x = pos
			return x, self._y(x)
		else:
			raise TypeError('pos must be an int or tuple')

	def _y(self, x: int) -> int:
		"""find the lowest empty row for column x"""
		# start from the bottom and work up
		for y in range(self.height-1, -1, -1):
			if self[x, y] == 0:
				return y
		raise ValueError('Column is full.')

	def _pos_diagonals(self):
		"""Get positive diagonals, going from bottom-left to top-right."""
		for di in ([(j, i - j) for j in range(self.width)] for i in range(self.width + self.height - 1)):
			yield [self[i, j] for i, j in di if i >= 0 and j >= 0 and i < self.width and j < self.height]

	def _neg_diagonals(self):
		"""Get negative diagonals, going from top-left to bottom-right."""
		for di in ([(j, i - self.width + j + 1) for j in range(self.height)] for i in range(self.width + self.height - 1)):
			yield [self[i, j] for i, j in di if i >= 0 and j >= 0 and i < self.width and j < self.height]

	def _full(self) -> bool:
		"""Check if Board is full."""
		for x in range(self.width):
			if self[x, 0] == 0:
				return False
		return True