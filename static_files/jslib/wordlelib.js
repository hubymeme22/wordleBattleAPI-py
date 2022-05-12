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
	const QValue = window.localStorage.getItem('Q');
	const myValue = window.localStorage.getItem('my_val');

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
		console.log('Agreed upon key : ' + response);
		window.localStorage.setItem('agreed_key', response);

		if (response == 'None')
			console.error('The tokens in the localstorage is corrupted, it is advised to reset again.');
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

////////////////////
//   Wordle API   //
////////////////////
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

	guess(wordGuess, callback=(arr_data) => {}) {
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
}