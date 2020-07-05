from KorosenseiBot import Bot
from .C4 import Connect4

def setup(bot: Bot):
	bot.add_cog(Connect4(bot))