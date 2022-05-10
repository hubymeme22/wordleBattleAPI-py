'''
WordleBattle is a wordle-like game which supports single and multiplayer.
By: Hubert F. Espinola I
'''
from os.path import isfile
from random import choice, shuffle

'''
Loads the text contained in the file, each word is separated
by a new line.
'''
class TextFileLoader:
	def __init__(self, filename : str='') -> None:
		self.filedata = []

		if (filename != ''):
			self.loadTextFile(filename)

	def loadTextFile(self, filename : str) -> None:
		self.filedata = TextFileLoader.loadParse(filename)

	@staticmethod
	def loadParse(filename) -> None:
		if (isfile(filename)):
			filedata = open(filename, 'r').read().split('\n')
			return filedata
		raise Exception('TextFileLoader.FileNonExistent')



'''
Class that checks the status of the characters
in the alphabet, status corresponds to the ff:

0 - letter is not used in the word
1 - letter is uesd but not in proper position
2 - letter is used and is on its proper position
'''
class AvailableLettersChecker:
	def __init__(self) -> None:
		self.capitalLetters = {
			'A' : 0, 'B' : 0, 'C' : 0, 'D' : 0, 'E' : 0,
			'F' : 0, 'G' : 0, 'H' : 0, 'I' : 0, 'J' : 0,
			'K' : 0, 'L' : 0, 'M' : 0, 'N' : 0, 'O' : 0,
			'P' : 0, 'Q' : 0, 'R' : 0, 'S' : 0, 'T' : 0,
			'V' : 0, 'W' : 0, 'X' : 0, 'Y' : 0, 'Z' : 0
		}

	def rightPosition(self, character : str):
		self.capitalLetters[character] = 2

	def wrongPosition(self, character : str):
		self.capitalLetters[character] = 1

	def getCorrect(self):
		output = {}
		for key in self.capitalLetters:
			if (self.capitalLetters[key] == 2):
				output[key] = 2
		return output

	def getSemiCorrect(self):
		output = {}
		for key in self.capitalLetters:
			if (self.capitalLetters[key] == 2):
				output[key] = 2
			elif (self.capitalLetters[key] == 1):
				output[key] = 1
		return output

	def getStatus(self):
		return self.capitalLetters



'''
Class that is responsible for scoring the input on each
word that is assigned by the wordle.
'''
class Checker(AvailableLettersChecker):
	def __init__(self, currentWord : str='', attempts : int=0) -> None:
		super().__init__()

		self.currentWord = currentWord
		self.wordLength  = len(currentWord)
		self.attemptFlag = False
		self.maxAttempt  = attempts
		self.attempts    = 0
		self.repetition  = 0

		if (attempts > 0):
			self.attemptFlag = True

	# removes the character matched to avoid
	# confusion in matching the characters
	def __remove_chr(self, cpyCurrent : list, character : str):
		cpyCurrent.remove(character)
		return cpyCurrent

	# resets the word to be guessed
	def reset(self):
		self.repetition += 1
		self.attempts = 0

	# checks the word provided
	def checkWord(self, word : str) -> dict:
		word = word.upper()
		output = [0 for i in range(len(word))]

		if (self.attemptFlag and self.attempts >= self.maxAttempt):
			print('Max attempts exceeded')
			return []

		cpyCurrent = list(self.currentWord)
		for i in range(len(word)):
			if (word[i] == self.currentWord[i]):
				cpyCurrent = self.__remove_chr(cpyCurrent, word[i])
				self.rightPosition(word[i])
				output[i] = 2

			elif (word[i] in self.currentWord[i]):
				cpyCurrent = self.__remove_chr(cpyCurrent, word[i])
				cpyCurrent = self.wrongPosition(word[i])
				output[i] = 1

		self.attempts += 1
		return output

'''
Simple implementation of wordle mechanics
	filename : name of file containing the words that will be guessed.
	wordnums : number of words that the user will be guessed.
	attempts : max number of guessing
'''
class Wordle(TextFileLoader):
	def __init__(self, filename: str='', wordnums : int=0, attempts : int=4) -> None:
		super().__init__(filename)

		if (wordnums > len(self.filedata)):
			raise Exception('[LoadingError] Number of word exceeds the number of words inside the file')

		self.wordCheckers  = []
		for i in range(wordnums):
			generatedWord = choice(self.filedata)
			self.filedata.remove(generatedWord)
			self.wordCheckers.append(Checker(generatedWord, attempts))

	def getCurrentWordLength(self) -> int:
		if (len(self.wordCheckers) > 0): return self.wordCheckers[0].wordLength
		return 0

	def resetCurrent(self) -> None:
		self.wordCheckers[0].reset()

	def guess(self, word : str) -> list:
		# to secure that the word has the matched length
		answerWordLength = self.getCurrentWordLength()
		if (len(word) <= answerWordLength):
			return self.wordCheckers[0].checkWord(word)

		return self.wordCheckers[0].checkWord(word[:answerWordLength])

	def proceed(self) -> None:
		self.wordCheckers[1:]


if __name__ == '__main__':
	Battle = Wordle(r'C:\Users\HueHueberry\OneDrive\Desktop\Advanced OOP Project\webapp\modules\sample.txt', 3, 3)

	print('The current length of word is :', Battle.getCurrentWordLength())
	while True:
		sample = input('Guess : ')
		output = Battle.guess(sample)
		print(output)

		if (output == []):
			print('Reseting the game')
			Battle.resetCurrent()