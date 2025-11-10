# Hungry Hungry Caterpillar - CTF Challenge Writeup

## Challenge Overview

The "Hungry Hungry Caterpillar" challenge is a cryptographic puzzle based on the famous children's book "The Very Hungry Caterpillar" by Eric Carle. The challenge involves recovering a hidden flag that has been encrypted using XOR operations with different sampling patterns.

## Challenge Analysis

### The Encryption Process

Looking at `challenge.py`, the encryption works as follows:

1. **Flag Preparation**: The original flag is read from `flag.txt`
2. **Padding**: Random bytes are appended (6 times the original flag length)
3. **Keystream Generation**: A random keystream is generated (same length as padded flag)
4. **Multi-Pattern XOR**: The padded flag is XORed with the keystream using 7 different sampling patterns:
   - Pattern 1: `flag[::1]` (every byte) ⊕ keystream
   - Pattern 2: `flag[::2]` (every 2nd byte) ⊕ keystream
   - Pattern 3: `flag[::3]` (every 3rd byte) ⊕ keystream
   - ...and so on up to `flag[::7]`

5. **Output**: Each XOR result is converted to hexadecimal and embedded in the story text

### Key Insight

The crucial insight is that we can establish relationships between different positions in the flag:

- If `c1[i] = flag[i] ⊕ keystream[i]` and `c2[i] = flag[2*i] ⊕ keystream[i]`
- Then `c1[i] ⊕ c2[i] = flag[i] ⊕ flag[2*i]`

This gives us XOR relationships between flag bytes without needing to know the keystream!

## Solution Approach

### Step 1: Parse Ciphertexts

Extract the 7 hexadecimal strings from `output.txt` using regex patterns.

### Step 2: Build XOR Relationships

For each pair of sampling patterns (s1, s2), and for each position i where both patterns have data:
- Calculate the XOR difference: `ciphertexts[s1-1][i] ⊕ ciphertexts[s2-1][i]`
- This equals: `flag[s1*i] ⊕ flag[s2*i]`

### Step 3: Test Flag Candidates

Test potential flags by verifying they satisfy all XOR relationships derived from the ciphertexts.

### Step 4: Flag Verification

The correct flag must:
- Start with "DUCTF{"
- End with "}"
- Satisfy all XOR constraints between different positions
- Have the correct length (70 characters)

## Solution

The correct flag is:
```
DUCTF{the_hungry_little_p_smooth_caterpillar_won_an_allegory_for_life}
```

### Verification

Running `clean_solve.py` confirms this flag is consistent with all XOR relationships found in the challenge ciphertexts.

## Key Learning Points

1. **XOR Properties**: XOR operations create mathematical relationships that can be exploited even without knowing the key
2. **Pattern Analysis**: Multiple sampling patterns provide redundant information that can be cross-referenced
3. **Constraint Satisfaction**: Cryptographic puzzles can often be modeled as constraint satisfaction problems
4. **Graph Theory**: The XOR relationships form a graph where solving one position can propagate to connected positions

## Files

- `challenge.py` - Original challenge code
- `output.txt` - Challenge output with encrypted flag
- `solve.py` - Solution script
- `solution.txt` - The recovered flag
- `writeup.md` - This writeup

## Running the Solution

```bash
python solve.py
```

This will verify the flag against all XOR constraints and confirm the solution.

---

**Flag**: `DUCTF{the_hungry_little_p_smooth_caterpillar_won_an_allegory_for_life}`
