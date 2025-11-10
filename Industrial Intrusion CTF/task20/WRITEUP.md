# Task 20: AES-GCM Nonce Reuse Attack - Writeup

## Challenge Overview
Task 20 exploited a critical vulnerability in AES-GCM: **nonce reuse**. The challenge provided:
- Two encrypted packet files: `cipher1(1).bin` and `cipher2(1).bin`
- Known plaintext for the first packet
- Both packets encrypted with the same nonce (fatal security flaw)

## Vulnerability Explanation

AES-GCM security critically depends on **never reusing nonces**. When the same nonce is used with the same key:
- The keystream becomes identical for both encryptions
- An attacker can XOR the ciphertexts to eliminate the keystream
- If one plaintext is known, the other can be recovered

## Attack Methodology

### File Structure Analysis
Each packet file contains:
```
[16 bytes nonce] || [96 bytes ciphertext] || [16 bytes GCM tag]
```

### Mathematical Foundation
For AES-GCM with nonce reuse:
- `C1 = P1 ⊕ Keystream`
- `C2 = P2 ⊕ Keystream` (same keystream due to nonce reuse)

Therefore: `C1 ⊕ C2 = P1 ⊕ P2`

If we know P1, we can recover P2: `P2 = P1 ⊕ C1 ⊕ C2`

### Known Plaintext
The first packet contained telemetry data:
```
BEGIN TELEMETRY VIRELIA;ID=ZTRX0110393939DC;PUMP1=OFF;VALVE1=CLOSED;PUMP2=ON;VALVE2=CLOSED;END;
```
(Padded to exactly 96 bytes with a null byte)

## Solution Implementation

```python
def solve_aes_gcm_nonce_reuse(file1_path, file2_path, known_plaintext_str):
    # Read both encrypted packet files
    with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
        packet1_data = f1.read()
        packet2_data = f2.read()

    # Extract 96-byte ciphertexts (skip 16-byte nonce, ignore 16-byte tag)
    ciphertext1 = packet1_data[16:112]
    ciphertext2 = packet2_data[16:112]

    # Convert known plaintext to bytes
    plaintext1 = known_plaintext_str.encode('utf-8')

    # Perform XOR attack: P2 = P1 ⊕ C1 ⊕ C2
    recovered_plaintext_bytes = bytes([
        p1_byte ^ c1_byte ^ c2_byte
        for p1_byte, c1_byte, c2_byte in zip(plaintext1, ciphertext1, ciphertext2)
    ])

    return recovered_plaintext_bytes.decode('utf-8')
```

## Results
The attack successfully recovered the second packet's plaintext:

```
BEGIN TELEMETRY VIRELIA;ID=TRX0110393939DC;PUMP=ON;VALVE=OPEN;TEMP=1.0;KILL=THM{Echo_Telemetry}
```

**Flag**: `THM{Echo_Telemetry}`

## Key Takeaways
- **Nonce Uniqueness is Critical**: Never reuse nonces in AES-GCM
- **Cryptographic Vulnerabilities**: Small implementation errors can completely break security
- **Known Plaintext Attacks**: Having partial knowledge can lead to full recovery

## Tools & Techniques Used
- **Binary File Analysis**: Understanding packet structure and data extraction
- **XOR Cryptanalysis**: Exploiting keystream reuse vulnerabilities
- **Python Byte Operations**: Manipulating binary data for cryptanalysis

## Running the Solution

```bash
python solver.py
```

This will:
1. Read both cipher files
2. Extract the ciphertext portions
3. Perform the XOR attack using the known plaintext
4. Display the recovered plaintext containing the flag

## Files in this Directory
- `solver.py` - The main attack script
- `cipher1(1).bin` - First encrypted packet (with known plaintext)
- `cipher2(1).bin` - Second encrypted packet (target for recovery)

## Technical Details

### AES-GCM Overview
- **Galois/Counter Mode (GCM)** provides both encryption and authentication
- Uses a nonce (number used once) to ensure security
- **Critical requirement**: Nonces must NEVER be reused with the same key

### The Attack Process
1. **Nonce Extraction**: Both files start with the same 16-byte nonce
2. **Ciphertext Extraction**: Extract the 96-byte payload from each file
3. **XOR Operation**: Leverage the mathematical property that `C1 ⊕ C2 = P1 ⊕ P2`
4. **Plaintext Recovery**: Since we know P1, we can solve for P2

### Why This Attack Works
When nonces are reused in AES-GCM:
- The same keystream is generated for both encryptions
- XORing the ciphertexts cancels out the keystream
- This reduces the problem to a simple XOR cipher with known plaintext
- The attack completely bypasses the encryption without needing the key

### Security Implications
This vulnerability demonstrates why:
- Cryptographic implementations must be perfect, not just "good enough"
- Nonce management is as critical as key management
- Even authenticated encryption can fail catastrophically with improper usage
- Code reviews and security audits are essential for cryptographic systems 