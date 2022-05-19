'''
Session handler for each users in WordleBattle. This supports
both duel battle and singleplayer.

By: Hubert F. Espinola I
'''
from Wordle import Wordle
import random
import string


# Handles user and their specified wordle object
# the 'key' also acts as user 'token' which identifies
# the user and the game he/she's playing.
class UserHandler:
	def __init__(self, fpath : str, numOfWordsToGuess : int, attempts : int=6) -> None:
		self.fpath = fpath
		self.numOfWordsToGuess = numOfWordsToGuess
		self.attempts = attempts

		self.userMap = {'key' : Wordle(fpath, numOfWordsToGuess, attempts)}

	# generates key available for the session
	def generateKey(self) -> str:
		keyGen = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
		if (keyGen not in self.userMap):
			return keyGen
		return self.generateKey()

	# retrieves the wordle object of the specified user
	def getWordle(self, token : str) -> Wordle:
		if (token in self.userMap):
			return self.userMap[token]
		return None

	# registers the token and maps on empty Wordle object
	def register(self, key : str):
		if (key not in self.userMap):
			print('KEY IS REGISTERED!')
			self.userMap[key] = Wordle(self.fpath, self.numOfWordsToGuess, self.attempts)

		print('KEY REGISTRATION DONE')

	# assign current token's wordle to the new token
	def switchTokenWordle(self, oldToken : str, newToken : str) -> bool:
		if (oldToken in self.userMap):
			currentTokenWordle = self.getWordle(oldToken)
			self.userMap[newToken] = currentTokenWordle

			self.userMap.pop(oldToken)
			return True
		return False

	# checks if the token is registered
	def isRegistered(self, key : str) -> bool:
		if (key in self.userMap):
			return True
		return False
