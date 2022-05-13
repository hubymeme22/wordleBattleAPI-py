from Sessions import UserHandler
from Wordle import Wordle

class SingleSessionHandler(UserHandler):
	def __init__(self, fpath: str, numOfWordsToGuess: int, attempts : int=6) -> None:
		super().__init__(fpath, numOfWordsToGuess, attempts)

	def guess(self, token : str, answer : str) -> list:
		if (token in self.userMap):
			userWordle = self.getWordle(token)
			output = userWordle.guess(answer)
			print(f'[User {token}] Answer status : {output}')

			# meaning, the answer is correct
			count_correct = output.count(2)
			if (count_correct == len(output)):
				userWordle.proceed()

			# after proceeding, if the size of the word is 0
			# this means that all the challenge is completed
			# returns specific unique list for indication
			if (len(userWordle.wordCheckers) <= 0):
				return [-1]
			return output

		return []

	# call this again to retry to solve the current word again
	# returns '1' if there's no problem in reseting
	def tryAgain(self, token : str) -> str:
		if (token in self.userMap):
			userWordle = self.getWordle(token)
			userWordle.resetCurrent()
			return '1'
		return '0'

	# resest and gives a new set of words for this token
	def reset(self, token : str) -> str:
		if (token in self.userMap):
			self.userMap[token] = Wordle(self.fpath, self.numOfWordsToGuess)
			return '1'
		return '0'