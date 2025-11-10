# Task 19: AES-CBC Decryption Challenge - Writeup

## Challenge Overview
Task 19 involved decrypting an encrypted log file (`log.enc`) using AES encryption in CBC mode. The challenge provided:
- **Passphrase**: `VIRELIA-WATER-FAC`
- **Encryption Mode**: AES-CBC 
- **Key Length**: 256 bits (32 bytes)
- **IV**: Fixed IV of 16 zero bytes

## Analysis & Approach

### Key Derivation
The critical part of this challenge was understanding how the encryption key was derived from the passphrase. After analysis, we determined that:

1. **Hash Function**: SHA-256 was used for key derivation
2. **Method**: Iterative hashing similar to EVP_BytesToKey
3. **Process**: 
   - Start with empty `prev_hash_block`
   - Hash `prev_hash_block + passphrase` using SHA-256
   - Append result to derived bytes
   - Repeat until we have enough bytes for the key

### Decryption Process

```python
def derive_key(password: bytes, key_len: int) -> bytes:
    """Generate key from passphrase using SHA-256."""
    derived_bytes = b''
    prev_hash_block = b''
    while len(derived_bytes) < key_len:
        m = hashlib.sha256()
        m.update(prev_hash_block + password)
        prev_hash_block = m.digest()
        derived_bytes += prev_hash_block
    return derived_bytes[:key_len]
```

The decryption steps were:
1. Read the encrypted file (`log.enc`)
2. Derive the 32-byte AES key from the passphrase
3. Use AES-CBC with the fixed zero IV to decrypt
4. Remove PKCS#7 padding from the result

## Solution
Running the decryption script revealed the flag:

```
CMD:SHUTDOWN
THM{cbc_cl3ar4nce_gr4nt3d_10939}
```

**Flag**: `THM{cbc_cl3ar4nce_gr4nt3d_10939}`

## Key Takeaways
- **Key Derivation Matters**: Understanding the exact key derivation method is crucial
- **IV Security**: Fixed IVs in CBC mode reduce security but didn't prevent decryption here
- **Algorithm Analysis**: Sometimes you need to try different hash functions (MD5 vs SHA-256)

## Tools & Techniques Used
- **Python Cryptography Libraries**: `pycryptodome` for AES operations
- **Padding Analysis**: PKCS#7 padding removal in CBC mode
- **Hash Function Analysis**: Testing different key derivation methods

## Running the Solution

```bash
python decrypt.py
```

This will:
1. Decrypt `log.enc` using the derived key
2. Save the decrypted result to `decrypted_log.txt`
3. Display the flag in the console output

## Files in this Directory
- `decrypt.py` - The main decryption script
- `log.enc` - The encrypted log file to decrypt
- `decrypted_log.txt` - The output file containing the decrypted content

## Technical Details

### AES-CBC Mode
- **Cipher Block Chaining (CBC)** mode requires an initialization vector (IV)
- In this case, a fixed IV of 16 zero bytes was used
- CBC mode is vulnerable to certain attacks when IVs are predictable, but that wasn't the focus here

### Key Derivation Security
The challenge demonstrated the importance of understanding key derivation:
- Initially might try MD5-based derivation (common in older systems)
- The correct solution required SHA-256
- This highlights how small implementation details can be crucial for cryptanalysis 