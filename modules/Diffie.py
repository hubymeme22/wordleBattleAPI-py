# Simple implementation of diffie hellman key exchange
# By: Hubert F. Espinola I
import random

class Diffie:
	__prime_list = [27, 13, 19, 11]

	def __init__(self, PValue : int, QValue : int) -> None:
		self.PValue  = PValue
		self.QValue  = QValue
		self.myValue = random.randint(22222, 999999)

		self.myMixedVal    = None
		self.calculatedKey = None

		self.otherVal = None

	def getMixedVal(self):
		if (self.myMixedVal == None):
			self.myMixedVal = pow(self.PValue, self.myValue, self.QValue)
		return self.myMixedVal

	def calculateKey(self, othersMixedValue : int):
		if (self.calculatedKey == None):
			self.calculatedKey = pow(othersMixedValue, self.myMixedVal, self.QValue)		
		return self.calculatedKey

	def getCurrentKey(self):
		return self.otherVal

	@staticmethod
	def getRandomPrime():
		return random.choice(Diffie.__prime_list)

	@staticmethod
	def getCharHex(key : int):
		keyHex = hex(key).replace('0x', '')
		output = []

		if (len(keyHex) % 2 != 0):
			keyHex = '0' + keyHex

		for i in range(0, len(keyHex), 2):
			print(keyHex[i] + keyHex[i + 1])
			output.append(chr(int(keyHex[i] + keyHex[i + 1], base=16)))

		return output