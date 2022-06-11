# wordlelib.js

This JavaScript library is made for packing all the needed requests for the `WordleBattle-API`. So, instead of making your own requests from scratch, now all you need to do is call the functions inside this library.

<br/>

# Main Functions and Uses
**`TokenRequestMulti()`** - Requests for valid token from the server and a random prime P. The token and prime P will be stored in the `window.localStorage`. The token will be used for session and tracking player's account, while the prime P, on the other hand, will be used for encrypted credential transfer (weak encryption btw).

<br/>

**`handshake()`** - This function finalizes the [Diffie Hellman key exchange]("https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange") and derives the key that will be used in encrypted credentials transfer. Obviously, we have to call `TokenRequestMulti()` before using this, since we need the prime number P first before deriving the key. Example usage below:

```JavaScript
TokenRequestMulti();
setTimeout(function() {
	handshake();
}, 500);

```

we delay calling the `handshake()` by 500ms to let the `TokenRequestMulti()` finish writing the token and prime P in the `window.localStorage` first. Other than finalizing the key exchange, in server-side, the handshake request also finalizes the token registration (final valdation of token).

<br/>

**`flush_enctokens()`** - Flushes the tokens, P, Q, username, and key from the `window.localStorage`. This function is used for reseting the game session in the browser. This can be used if a player has to log-out from the game. Example:

```JavaScript
function logout() {
	flush_enctokens();
}
```

<br/>

**`loginCreds(username, password, enc_callback, resp_callback)`** - Logs in the account of user. This function has four (4) parameters: username, password, enc_callback, and resp_callback.
* `username` - Username of the wordleBattle account.
* `password` - Password of the wordleBattle account.
* `enc_callback` - An encryption callback, this callback has one parameter called `data` where username and password will be passed on. This function must return an encrypted version of the `data`. By default, this callback uses an `xorEncryption(data)` function.
* `resp_callback` - A callback that has parameter `response` which the server response code will be stored. Response code are the ff:
	* *`successful`* - The account is logged in successfully.
	* *`unsucessful`* - Credentials supplied either does not exist or wrong password is used.

Example Usage:

```JavaScript
TokenRegisterMulti();
setTimeOut(handshake, 500);

button.onclick = () => {
	// use the xorEncryption function
	loginCreds('username', 'password', undefined, (response) => {
		if (respones === 'successful')
			alert('Successfully logged in!');
		else
			alert('Wrong credentials'); 
	});
}
```
<br/>

**`registerCreds(username, password, enc_callback, resp_callback)`** - Registers the specified credentials to the server. The parameters here are the same as the `loginCreds(...)` function above, the server response is also the same but has additional response *`usererror`* which means that the username that is attempting to be registered is already registered.

<br/>

**`shuffleWordlist(callback)`** - Shuffles the wordlist and also resets the user's status (wordlist and level). The callback has parameter `data`, which the server response will be stored. The server response can be:
* `usererror` - The current user is not logged in properly.
* `0` - The token is not registered.
* `1` - The reset/shuffle is executed properly.

<br/>

**`retryWord(callback)`** - Requests the server to reset the attempts made by the user (asks the server to try solve the same problem again). The callback also has the same parameter `data` that contains the server responses which are the same as `shuffleWordlist(...)` (`0` and `1`, but has additional response code: `-1` which means that the current token is corrupted)

<br/>

**`getSavedGameStatus(callback)`** - Requests for the last game state of the user. The callback also has the same parameter `data`, which contains a json response from the server. This json response contains: points, previous word attempts, and the attempt states.