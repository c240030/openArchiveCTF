# Industrial Intrusion CTF - Writeups

This repository contains solutions and writeups for cryptographic challenges from the Industrial Intrusion CTF.

## Tasks Completed

### Task 19: AES-CBC Decryption Challenge
- **Location**: [`task19/WRITEUP.md`](task19/WRITEUP.md)
- **Challenge Type**: AES-CBC decryption with key derivation
- **Flag**: `THM{cbc_cl3ar4nce_gr4nt3d_10939}`

**Quick Summary**: Decrypt an encrypted log file using AES-CBC with a passphrase-derived key. The key challenge was understanding the SHA-256-based key derivation process.

### Task 20: AES-GCM Nonce Reuse Attack
- **Location**: [`task20/WRITEUP.md`](task20/WRITEUP.md)
- **Challenge Type**: Cryptographic vulnerability exploitation
- **Flag**: `THM{Echo_Telemetry}`

**Quick Summary**: Exploit a nonce reuse vulnerability in AES-GCM to recover plaintext from encrypted packets using XOR cryptanalysis.

## Running the Solutions

Navigate to each task directory and run the respective Python scripts:

```bash
# Task 19
cd task19
python decrypt.py

# Task 20
cd task20
python solver.py
```

## Key Learning Points

- **Cryptographic Implementation Matters**: Small details in key derivation and nonce management can completely break security
- **Algorithm Analysis**: Understanding the exact cryptographic processes is crucial for successful attacks
- **XOR Cryptanalysis**: Demonstrates how implementation flaws can reduce strong encryption to simple XOR ciphers

## Repository Structure

```
industrial-intrusion-ctf/
├── task19/
│   ├── WRITEUP.md          # Detailed Task 19 writeup
│   ├── decrypt.py          # AES-CBC decryption script
│   ├── log.enc             # Encrypted log file
│   └── decrypted_log.txt   # Decrypted output
├── task20/
│   ├── WRITEUP.md          # Detailed Task 20 writeup
│   ├── solver.py           # GCM nonce reuse attack script
│   ├── cipher1(1).bin      # First encrypted packet
│   └── cipher2(1).bin      # Second encrypted packet
└── WRITEUP.md              # This overview file
``` 