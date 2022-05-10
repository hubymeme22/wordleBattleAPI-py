function packedRequest_GET(host, callback=(data) => {}) {
	fetch(host)
		.then(response => response.text())
		.then(data => {
			callback(data);
		});
}


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


class InterpreterWordleAPI {
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

	guess(wordGuess) {
		var host = window.location.origin;
		host += '/single/guess/' + this.token + '/' + wordGuess;

		var output;
  		packedRequest_GET(host, (data) => {
			this.interpretAPI(wordGuess, data);
			output = JSON.parse(data);

			console.log(output);
		});

		return output;
	}

	getAlphabetStatus() {
		return this.alphabet;
	}

	retrieveToken() {
		this.token = window.localStorage.getItem('token');
	}
}