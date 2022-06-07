'''
WordleBattle is a wordle-like game which supports single and multiplayer.
By: Hubert F. Espinola I
'''
from os.path import isfile
from random import choice

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
	def __remove_chr(self, cpyCurrent : list, idx : int):
		# replace with special character to avoid index conflict
		cpyCurrent[idx] = chr(0)
		return cpyCurrent

	# resets the word to be guessed
	def reset(self):
		self.repetition += 1
		self.attempts = 0

	# checks the word provided
	def checkWord(self, word : str) -> list:
		word = list(word.upper())
		output = [0 for i in range(len(word))]

		if (self.attemptFlag and self.attempts >= self.maxAttempt):
			print('Max attempts exceeded')
			return [-2]

		cpyCurrent = list(self.currentWord)

		# loop for checking the right position first
		used_index = []
		for i in range(len(word)):
			if (word[i] == cpyCurrent[i]):
				cpyCurrent = self.__remove_chr(cpyCurrent, i)
				used_index.append(i)
				output[i] = 2

		# loop for checking the wrong position
		for i in range(len(word)):
			if (i in used_index):
				continue

			if (word[i] in cpyCurrent):
				idx = cpyCurrent.index(word[i])
				cpyCurrent = self.__remove_chr(cpyCurrent, idx)
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
	def __init__(self, filename: str='', wordnums : int=0, attempts : int=6) -> None:
		super().__init__(filename)

		if (wordnums > len(self.filedata)):
			raise Exception('[LoadingError] Number of word exceeds the number of words inside the file')

		self.points = 0					# current point of the user
		self.respState = []				# the state of server's response on the last word
		self.wordState = []				# answer state (can be loaded back)

		self.wordDictionary = self.filedata.copy()
		self.wordCheckers  = []
		for i in range(wordnums):
			generatedWord = choice(self.filedata)
			self.filedata.remove(generatedWord)
			self.wordCheckers.append(Checker(generatedWord, attempts))

	def getCurrentWordLength(self) -> int:
		if (len(self.wordCheckers) > 0): return self.wordCheckers[0].wordLength
		return 0

	def resetCurrent(self) -> None:
		self.respState = []
		self.wordState = []
		self.wordCheckers[0].reset()

	def guess(self, word : str) -> list:
		# check if there's no words left to be guessed
		if (len(self.wordCheckers) == 0):
			return [-3]

		# check if the word guessed is in the dictionary
		print(self.wordDictionary)
		if (word not in self.wordDictionary):
			return [-4]

		# to secure that the word has the matched length
		answerWordLength = self.getCurrentWordLength()
		arr = []
		if (len(word) <= answerWordLength):
			arr = self.wordCheckers[0].checkWord(word)
			self.wordState.append(word)
		else:
			targetWord = word[:answerWordLength]
			arr = self.wordCheckers[0].checkWord(targetWord)
			self.wordState.append(targetWord)

		# added process to save the players
		# last game state
		if ((1 not in arr) and(0 not in arr)):
			self.points += 1
			self.wordState = []
			self.respState = []
		else:
			self.respState.append(arr)

		return arr


	def getSavedGameState(self) -> dict:
		json_format = {
			'points'   : self.points,
			'resp'     : self.respState,
			'state'    : self.wordState
		}
		return json_format

	def proceed(self) -> None:
		self.wordCheckers = self.wordCheckers[1:]