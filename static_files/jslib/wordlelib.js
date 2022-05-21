/////////////////////////////////
//    Diffie Encryption part   //
////////////////////////////////
// generates a random prime P
function getRandomPrime() {
	// local method array
	prime_list = [5n, 7n, 11n, 13n, 17n, 19n, 23n, 29n, 31n, 37n, 41n, 43n, 47n, 53n, 59n, 61n, 67n, 71n, 73n, 79n, 83n, 89n, 97n]
	random_index = Math.floor(Math.random() * prime_list.length)

	return prime_list[random_index]
}

// calculates big integer power with modulo n (if needed)
function bigIntPow(a, b, n=0n) {
	output = 1n
	for (var i = 0; i < b; i++)
		output *= a

	if (n != 0n)
		return output % n
	return output
}

// generates the P^AmodQ
function getMixedVal() {
	const PValue = BigInt(window.localStorage.getItem('P'));
	const QValue = BigInt(window.localStorage.getItem('Q'));
	const myValue = BigInt(window.localStorage.getItem('my_val'));

	if (PValue == null) console.error('No PValue found in localstorage');
	if (QValue == null) console.error('No QValue found in localstorage');
	if (myValue == null) console.error('No Generated Value found in localstorage');

	return bigIntPow(PValue, myValue, QValue)
}

// gets the P^BmodQ of the server
function calculateKey(otherValue) {
	const QValue = BigInt(window.localStorage.getItem('Q'));
	const myValue = BigInt(window.localStorage.getItem('my_val'));

	if (QValue == null) console.error('No QValue found in localstorage');
	if (myValue == null) console.error('No Generated Value found in localstorage');

	return bigIntPow(otherValue, myValue, QValue)
}


// just for diffie value A
function generateValue() {
	return Math.ceil( Math.random() * 5000);
}

////////////////////////////////////////
//    Modified GET and POST request   //
////////////////////////////////////////
function packedRequest_GET(host, callback=(data) => {}) {
	fetch(host)
		.then(response => response.text())
		.then(data => {
			callback(data);
		});
}

function packedRequest_POST(host, data, callback=(data) => {}) {
	fetch(host, {
		method: 'POST',
		body: data,
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
	})
		.then(response => response.text())
		.then(data => {
			callback(data);
		})
}

/////////////////////////////
//   Tokens and Sessions   //
/////////////////////////////
// requests for encrypted token (registers the token to the server)
// used for credential login
function tokenRequestMulti() {
	var host = window.location.origin;
	host += '/encrypted/request/token';

	var currentToken = window.localStorage.getItem('enc_token');
	if (currentToken === null) {
		packedRequest_GET(host, (data) => {
			const tokenPart = data.split(':')[0];
			const PrimePart = data.split(':')[1];

			window.localStorage.setItem('enc_token', tokenPart);
			window.localStorage.setItem('P', PrimePart);
		});
	}
}

// requests token for a single player
// (for keeping track of which game is being played)
function tokenRequestSingle() {
	var host = window.location.origin;
	var modified = host + '/request/stoken/';

	var currentToken = window.localStorage.getItem('token');
	if (currentToken === null) {
		packedRequest_GET(modified, (data) => {
			window.localStorage.setItem('token', data);
		});
	}
}

// checks if the current token in the localstorage is registered
// response = yes: the current token is registered
// response = no: the current token is not registered
function isTokenRegistered(callback=(response) => {}) {
	const token = window.localStorage.getItem('token');
	var host = window.location.origin + '/single/isregistered/' + token;
	packedRequest_GET(host, (response) => {
		// reset the token on localstorage
		if (response === 'no') {
			window.localStorage.removeItem('token');
			setTimeout(tokenRequestSingle, 500);
		}
	})
}


// finalize the encryption using this handshake
function handshake() {
	const PValue = window.localStorage.getItem('P');
	var QValue = window.localStorage.getItem('Q');

	// check first if all the parameters are set
	if (PValue == null) {
		console.error('Cannot start: Request for encrypted token from the server first!');
		return;
	}

	if (QValue == null) {
		QValue = getRandomPrime();
		window.localStorage.setItem('Q', QValue);
	}

	// if this is set, then there's an existing connection for the token
	var my_val = window.localStorage.getItem('my_val');
	if (my_val === null) {
		// generate a new value for our session
		my_val = generateValue();
		window.localStorage.setItem('my_val', my_val);
	}

	// gets the mixed value for client
	const myMixedValue = getMixedVal();

	// finalizes by registering the token
	const enc_token = window.localStorage.getItem('enc_token');
	const host = window.location.origin + '/encrypted/handshake/' + enc_token;
	var forged_request = `PAQ=${myMixedValue}&Q=${QValue}`;

	packedRequest_POST(host, forged_request, (response) => {
		if (response == 'None') {
			console.error('The tokens in the localstorage is corrupted.');
			console.log('Flushing and requesting again...');

			flush_enctokens();
			tokenRequestMulti();

			// delay some ms, to load the localStorage
			setTimeout(handshake, 500);
		} else {
			const calculatedKey = calculateKey(BigInt(response));
			window.localStorage.setItem('agreed_key', calculatedKey);	
		}
	});
}


function flush_enctokens() {
	window.localStorage.removeItem('enc_token');
	window.localStorage.removeItem('P');
	window.localStorage.removeItem('Q');
	window.localStorage.removeItem('my_val');
	window.localStorage.removeItem('agreed_key');
}

function flush_token() {
	window.localStorage.removeItem('token');
}

/////////////////////////////
//  Credentials and login  //
/////////////////////////////
// default encryption function that will be used
function xorEncrypt(data) {
	var key = parseInt(window.localStorage.getItem('agreed_key'));
	var token = window.localStorage.getItem('enc_token');

	var new_data = [];
	if (key != null && token != null) {
		for (var i = 0; i < data.length; i++)
			new_data.push( key ^ token.charCodeAt(i % token.length) ^ data.charCodeAt(i));
	}

	return JSON.stringify(new_data);
}

// login the credentials given
function loginCreds(username, password, encCallback=xorEncrypt, responseCallback=(response) => {}) {
	const encrypted_user = encCallback(username);
	const encrypted_pass = encCallback(password);
	const enc_token = window.localStorage.getItem('enc_token');

	const pckt_structure = `uno=${encrypted_user}&anji=${encrypted_pass}`;
	const host = window.location.origin + `/encrypted/login/${enc_token}`;

	if (enc_token != null)
		packedRequest_POST(host, pckt_structure, (response) => {
			if (response == 'successful')
				window.localStorage.setItem('user', username);

			responseCallback(response);
		});
	else
		console.error('enc_token is not established');
}

// registers the credentials given
function registerCreds(username, password, encCallback=xorEncrypt, responseCallback=(response) => {}) {
	const encrypted_user = encCallback(username);
	const encrypted_pass = encCallback(password);
	const enc_token = window.localStorage.getItem('enc_token');

	const pckt_structure = `uno=${encrypted_user}&anji=${encrypted_pass}`;
	const host = window.location.origin + `/encrypted/register/${enc_token}`;

	if (enc_token != null)
		packedRequest_POST(host, pckt_structure, (response) => {
			responseCallback(response);
		});
	else
		console.error('enc_token is not established');
}

function logoutCreds() {
	flush_enctokens();
	tokenRequestMulti();
	handshake();
}

//////////////////////////////
//   Encrypted Wordle API   //
//////////////////////////////
function userGuess(answer, callback=(response) => {}) {
	var username = window.localStorage.getItem('user');
	var host = window.location.origin + `/${username}/guess`;
	const token = window.localStorage.getItem('enc_token');

	if (username != null && token != null) {
		const pckt_structure = `token=${token}&answer=${answer}`;
		packedRequest_POST(host, pckt_structure, (response) => {
			callback(response);
		});
	}
}

////////////////////
//   Wordle API   //
////////////////////
// requests to retry the same problem again
function retryCurrent() {
	var token = window.localStorage.getItem('token');
	if (token != null){
		var host = window.location.origin + '/single/try_again/' + token;
		packedRequest_GET(host);
	}
}

function scramble() {
	var token = window.localStorage.getItem('token');
	if (token != null) {
		var host = window.location.origin + '/single/retry/' + token;
		packedRequest_GET(host);
	}
}

class SingleWordleAPI {
	constructor() {
		this.alphabet = {
			'A' : 0, 'B' : 0, 'C' : 0, 'D' : 0, 'E' : 0,
			'F' : 0, 'G' : 0, 'H' : 0, 'I' : 0, 'J' : 0,
			'K' : 0, 'L' : 0, 'M' : 0, 'N' : 0, 'O' : 0,
			'P' : 0, 'Q' : 0, 'R' : 0, 'S' : 0, 'T' : 0,
			'V' : 0, 'W' : 0, 'X' : 0, 'Y' : 0, 'Z' : 0
		};

		this.token = window.localStorage.getItem('token');
		this.host  = window.location.origin;
	}

	interpretAPI(input, outputAPI) {
		input = input.toUpperCase();
		var output = JSON.parse(outputAPI);

		for (var i = 0; i < output.length; i++) {
			var chr = input.charAt(i);
			this.alphabet[chr] = output[i];
		}
	}

	// returns: list of array with values:
	// [2] if the corresponding index of the answer is correct
	// [1] if the letter
	guess(wordGuess, callback=(arr_data) => {}) {
		// recheck if the token is already okay but cannot retrieve properly
		if (this.token === null) {
			isTokenRegistered(response => {
				if (response == 'yes')
					this.retrieveToken();
			});
		}

		var host = window.location.origin;
		host += '/single/guess/' + this.token + '/' + wordGuess;

		packedRequest_GET(host, (data) => {
			this.interpretAPI(wordGuess, data);
			const output = JSON.parse(data);
			callback(output);
		});
	}

	getAlphabetStatus() {
		return this.alphabet;
	}

	retrieveToken() {
		this.token = window.localStorage.getItem('token');
	}

	// makes sure that the object's token is same as the
	// object's token
	fixLocalObjToken() {
		const token = window.localStorage.getItem('token');
		if (this.token != token) {
			this.token = token;
		}
	}
}