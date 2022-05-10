'''
WordleBattle API

By:
	Hubert F. Espinola I
	Angelika T. Amatus
'''
from flask import Flask, send_from_directory
import sys

sys.path.append('./modules')
from SinglePlayerSession import SingleSessionHandler


SingleSession = SingleSessionHandler('sample.txt', 2)
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

#####################
#   POST Requests   #
#####################

#####################
#     Main part     #
#####################
if __name__ == '__main__':
	app.debug = True
	app.run('localhost', 5050)