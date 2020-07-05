from NeoBot import Neo
from .C4 import Connect4

def setup(bot: Neo):
	bot.add_cog(Connect4(bot))