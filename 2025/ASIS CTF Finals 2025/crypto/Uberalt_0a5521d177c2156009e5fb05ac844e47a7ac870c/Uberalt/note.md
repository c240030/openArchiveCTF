# TL;DR
This is an interactive RSA encryption service
- There is modulus n
- The parameter R that user can control
- The secret message which is generated (16 bytes) when the program starts
# Vuln
## Public exponent e is not safe
- Program uses timestamp of the current time as the public exponent. This means that attackers can easily guess e by take the real time when connect to the server.
## The prime generation process depends on parameter R
### Prime p
- `sub_2512((__int64)v12, ..., (int)(0.335 * (double)a3));` generates a random number `v12` of length 1/3 of number of bits required
- `s = sub_32AC(..., &v11, ...)` turns `v12` into `s`
- `__gmpz_import(a1, ..., s)` turns `s` into prime p
### Prime q
- Right after p is found, the program continues to use `v12` (the random number)
- `__gmpz_add(v10, v12, a4)` computes a middle value (`v10 = v12 + R`)
- `v13 = sub_32AC(..., &v9, ...)` uses the same transformation function as p above on `v10`. After that turn it to q, and take the next prime of q

# Summary/Solution/Attack Vector
- p is created from Transform(Seed)
- q is created from Transform(Seed +R)
- The transform function looks complex but it still preserves the properties of the low bits if we have a nice R. So one can try to pick a nice R that (Seed+R) wont change the low bits after going through the Transform function. This suggests using LLL
- Setup connection and get the public exponent -> Generate params and send R -> Use LLL to get p and q -> Calc d and decrypt ciphertext -> Get flag
