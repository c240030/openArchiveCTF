# ECB-A-TRON 9000 - Writeup

## Challenge Overview
This challenge exploits the fundamental weakness of ECB (Electronic Codebook) mode encryption: identical plaintext blocks produce identical ciphertext blocks. By carefully controlling our input, we can decrypt the secret message one character at a time.

## Understanding the Vulnerability
ECB mode encrypts each block independently. When we encrypt:
```
[our_input] + [secret_message]
```

If we can align the blocks properly, we can determine each character of the secret by brute forcing.

## The Attack Methodology
The challenge involved a step-by-step block-by-block attack against ECB mode encryption, where each block is 16 bytes.

### Step 1: Setting Up the Attack
Looking at the given file, we see a sequence from 15A to 0A, each with associated ciphertext blocks. By analyzing this pattern, we can reconstruct how the attack was performed.

### Step 2: Decryption Process
For each character position:

1. **Create a Target Ciphertext**: 
   - We input padding characters (A's) of a specific length to push the unknown character to the end of a block
   - For the first character: 15 A's, making the first block: AAAAAAAAAAAAAAA + [first_secret_char]

2. **Brute Force the Unknown Character**:
   - We try all possible characters at the end of our controlled block
   - For example: AAAAAAAAAAAAAAAA, AAAAAAAAAAAAAAAB, etc.
   - When the resulting ciphertext matches our target, we've found the correct character

3. **Build the Secret Character by Character**:
   - Once we know the first character (D), we move to the second
   - We use 14 A's, making the first block: AAAAAAAAAAAAAA + [known_char_D] + [second_secret_char]
   - For brute forcing: AAAAAAAAAAAAAADA, AAAAAAAAAAAAAADB, etc.
   - We continue this pattern for each subsequent character

### Step 3: Results from the File
Looking at the sequence in the provided file, we can see the discovered characters:

```
15A: D
14A: O
13A: N
12A: T
11A: U
10A: S
9A: E
8A: E
7A: C
6A: B
5A: P
4A: L
3A: E
2A: A
1A: S
0A: E
```

Reading from top to bottom gives us the secret message: "DONTUSEECBPLEASE"

## Flag
The final flag is: `DUCTF{DONTUSEECBPLEASE}`

## Conclusion
This challenge demonstrates the critical weakness in ECB mode encryption. When identical plaintext blocks produce identical ciphertext blocks, it allows attackers to perform these types of block-by-block attacks. This is why modern applications should never use ECB mode for encrypting sensitive data, and should instead use more secure modes like CBC, GCM, or CTR with proper initialization vectors.

The challenge name "ECB-A-TRON 9000" and the revealed message "DONTUSEECBPLEASE" both emphasize the security recommendation: Don't use ECB mode for encryption!

## Technical Details
- **Block Size**: 16 bytes (128 bits)
- **Encryption Algorithm**: Likely AES in ECB mode
- **Attack Type**: Known plaintext attack exploiting ECB mode's deterministic nature

This challenge is a practical demonstration of why textbooks and security experts always advise against using ECB mode in real-world applications.