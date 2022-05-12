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
SingleSession = SingleSessionHandler('sample.txt', 2)
EncryptedSession = EncSession('sample.txt', 2)

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

''' User requests for reset for the game '''
@app.route('/single/reset/<string:token>')
def resetCurrentGame(token):
	SingleSession.userMap[token].resetCurrent()
	return 'OK'

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