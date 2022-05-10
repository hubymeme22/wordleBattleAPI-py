// Simple implementation of DiffieHellman key exchange
// By: Hubert F. Espinola I


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



class Diffie {
	constructor(Pvalue, QValue) {
		this.Pvalue  = Pvalue
		this.QValue  = QValue
		this.myValue = BigInt(Math.floor(Math.random() * 500))
	}

	getMixedVal() {
		return bigIntPow(this.Pvalue, this.myValue, this.QValue)
	}

	calculateKey(otherValue) {
		return bigIntPow(otherValue, this.myValue, this.QValue)
	}
}