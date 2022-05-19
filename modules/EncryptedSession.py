from SinglePlayerSession import SingleSessionHandler
from Diffie import Diffie

'''
USER INFORMATION
contains.. you know, user information. Special
about this is that, this is where the
'''
class UserInfo:
	def __init__(self, username : str, password : str) -> None:
		self.__username = username
		self.__password = password
		self.settings = {
			'bgcolor' : '#FFFFFF'
		}

	# checks if this user has the same username
	def matchUser(self, username : str) -> bool:
		if (self.__username == username):
			return True

	# checks if this user has the same matched password
	def matchCreds(self, username : str, password : str) -> bool:
		if (self.__username == username and self.__password == password):
			return True
		return False

	# gets the username
	def getUsername(self) -> str:
		return self.__username

	# sets the setting from this user
	def setSetting(self, key : str, value) -> None:
		self.settings[key] = value








'''
USERDB (USER DATABASE)
This class handles user information
purposes: authentication, modification of user settings,
'''
class UserDB:
	# only allow one instance at a time
	def __init__(self) -> None:
		self.users = {'username' : UserInfo('username', 'password')}

	# checks the credentials of the user
	def checkCredentials(self, username : str, password : str):
		if (username in self.users):
			return self.users[username].matchCreds(username, password)
		return False

	# checks if the user exists in the list
	def checkUser(self, username : str) -> bool:
		if (username in self.users):
			return True
		return False

	# gets the user information of the current user
	def getUser(self, username : str) -> UserInfo:
		return self.users[username]

	# registers the credentials returns true if the username us valid
	# and false if the user already exists
	def register(self, username : str, password : str) -> bool:
		if (username not in self.users):
			self.users[username] = UserInfo(username, password)
			return True
		return False

	# change password

	# change settings

	# @staticmethod
	# def getInstance():
	# 	if (UserDB.__instance == None):
	# 		UserDB()
	# 	return UserDB.__instance


'''
AUTHENTICATION - Authenticates and maps the token to the user
slight modification and integration to encryption makes this class
more secured.
'''
class Authentication(SingleSessionHandler):
	__instance = None

	def __init__(self, fpath: str, numOfWordsToGuess: int, userDatabase : UserDB=None) -> None:
		super().__init__(fpath, numOfWordsToGuess)
		if (Authentication.__instance != None):
			raise Exception('InstanceCopyError: Only one instance is allowed')

		self.localUserDB = userDatabase
		self.userTokenMap = {'username' : 'token'}

	# manually connects the local user database object to this class
	def connectLocalDB(self, userDatabase : UserDB):
		self.localUserDB = userDatabase

	# sets the token for the user specified
	def setUserToken(self, username : str, token : str):
		# checks if the user is registered first in the localUserDatabase
		if (self.localUserDB.checkUser(username)):
			# check if an existing token is registered to this user
			# pass this session to the new token
			if (self.userMap[username] != None):
				self.switchTokenWordle(token, self.getUserToken(username))

			self.userTokenMap[username] = token
			super().register(token)

	# gets the token for this user
	def getUserToken(self, username : str) -> str:
		return self.userTokenMap[username]

	# gets the wordle object for this user
	def getUserWordle(self, username : str) -> str:
		return super().getWordle( self.getUserToken(username) )

	# logs in the user and registers its token to the account
	def login(self, username : str, password : str, token : str) -> bool:
		isValid = self.localUserDB.checkCredentials(username, password)
		if (isValid):
			self.setUserToken(username, token)
			return True
		return False


'''
Session handler for authentication and the actual game for multiplayer
'''
class EncSession(Authentication):
	def __init__(self, fpath: str, numOfWordsToGuess: int, userDatabase: UserDB = None) -> None:
		super().__init__(fpath, numOfWordsToGuess, userDatabase)
		self.pendingTokens = {'token' : 13}
		self.tokenDiffiePair = {'token' : Diffie(13, 13)}

	# generates a token for the user alongside the P
	def getToken(self) -> tuple[str, int]:
		token = super().generateKey()
		randomPrimeP = Diffie.getRandomPrime()

		# registers on pending handshake
		self.pendingTokens[token] = randomPrimeP
		return (token, randomPrimeP)

	# first handshake for the program
	# returns P^BmodQ for final key exchange
	def handshake(self, token : str, PAQ : int, Q):
		if (token in self.tokenDiffiePair):
			return self.tokenDiffiePair[token].getMixedVal()

		if (token in self.pendingTokens):
			primeP = self.pendingTokens[token]
			diffie = Diffie(primeP, Q)
			mixed_value = diffie.getMixedVal()

			# registers the diffie to the token
			diffie.calculateKey(PAQ)
			self.tokenDiffiePair[token] = diffie

			# register this to the parent normal Session
			super().register(token)
			return mixed_value

		return None

	# checks if the encrypted token is registered
	def isEncTokenRegistered(self, token : str) -> bool:
		if (token in self.tokenDiffiePair):
			return True
		return False

	# gets the diffie key of the current token
	def getKey(self, token : str) -> int:
		if (self.isEncTokenRegistered(token)):
			return self.tokenDiffiePair[token].getCurrentKey()
		return 0


	# FOR NOW uses basic xor encryption
	@staticmethod
	def encrypt(token : str, key : int, creds : str) -> bytes:
		return ''.join([chr( ord(creds[i]) ^ ord(token[i % 32]) ^ key ) for i in range(len(creds))])

	@staticmethod
	def decrypt(token : str, key : int, creds : str) -> bytes:
		return EncSession.encrypt(token, key, creds)