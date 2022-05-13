'''
WordleBattle API

By:
	Hubert F. Espinola I
	Angelika T. Amatus
'''
from flask import Flask, send_from_directory, request
import sys

sys.path.append('./modules')
from SinglePlayerSession import SingleSessionHandler
from EncryptedSession import EncSession, UserDB


# database for user information
UserDatabase = UserDB()

# Session handlers
SingleSession = SingleSessionHandler('sample.txt', 4)
EncryptedSession = EncSession('sample.txt', 4)

app = Flask(__name__)

####################
#   GET Requests   #
####################
@app.route('/')
def index():
	return 'Hello world!'

@app.route('/<path:path>')
def staticFileHandler(path):
	return send_from_directory('static_files', path)

############################
#   special GET requests   #
############################
''' Requests for session on single player '''
@app.route('/request/stoken/')
def sessionSingle():
	token = SingleSession.generateKey()
	SingleSession.register(token)

	return token

''' User guesses the answer '''
@app.route('/single/guess/<string:token>/<string:answer>')
def guessAnsSingle(token, answer):
	output = SingleSession.guess(token, answer)
	return str(output)

''' User requests for trying to solve the word again '''
@app.route('/single/try_again/<string:token>')
def tryAgain(token):
	return SingleSession.tryAgain(token)

''' User requests to scramble the set of words to solve '''
@app.route('/single/reset/<string:token>')
def resetWord(token):
	return SingleSession.reset(token)

''' User checks if the token is registered '''
@app.route('/single/isregistered/<string:token>')
def isRegistered(token):
	registered = SingleSession.isRegistered(token)
	if (registered):
		return 'yes'
	return 'no'

##############################
#   Encrypted GET Requests   #
##############################
''' Gets token for encrypted communications '''
@app.route('/encrypted/request/token')
def getEncryptedToken():
	token, P = EncryptedSession.getToken()
	return token + ':' + str(P)

#####################
#   POST Requests   #
#####################
''' Posts data for diffie hellman key exchange '''
@app.route('/encrypted/handshake/<string:token>', methods=['POST'])
def diffieHandshake(token):
	userMixedVal = request.form.get('PAQ')
	QValue = request.form.get('Q')

	if ((userMixedVal != None) and (QValue != None)):
		userMixedVal = int(userMixedVal)
		QValue = int(QValue)
		BMixed = EncryptedSession.handshake(token, userMixedVal, QValue)
		print(f'The calculated Bmixed is : {BMixed}')
		return str(BMixed)

	return 'UnknownParamError'


#####################
#     Main part     #
#####################
if __name__ == '__main__':
	app.debug = True
	app.run('localhost', 5050)