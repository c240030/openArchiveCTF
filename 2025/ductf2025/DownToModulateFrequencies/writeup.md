# DTMF Challenge Writeup

## Challenge Name: Down To Modulate Frequencies

## Description
The challenge presented us with a text file `dtmf.txt` containing a long string of numbers. The filename "Down To Modulate Frequencies" (DTMF) was a crucial hint pointing to Dual-Tone Multi-Frequency signaling used in touch-tone telephone systems.

## Understanding the Challenge

DTMF is a telecommunication signaling system using the voice-frequency band over telephone lines. Each key on a telephone keypad produces a tone that is the sum of two specific frequencies:

| | 1209 Hz | 1336 Hz | 1477 Hz | 1633 Hz |
|-------|-------|-------|-------|-------|
| **697 Hz** | 1 | 2 | 3 | A |
| **770 Hz** | 4 | 5 | 6 | B |
| **852 Hz** | 7 | 8 | 9 | C |
| **941 Hz** | * | 0 | # | D |

In the challenge, the string of numbers represented these frequency sums. For example:
- Key 2 = 697 Hz + 1336 Hz = 2033
- Key 6 = 770 Hz + 1477 Hz = 2247

Furthermore, the challenge used the old multi-tap text entry system used on phone keypads, where:
- Pressing key 2 once gives 'A'
- Pressing key 2 twice gives 'B'
- Pressing key 2 three times gives 'C'
- And so on...

## Solution Approach

1. First, we mapped the DTMF frequency sums to their corresponding keypad digits:
```python
CODE_TO_KEY = {
    '1906': '1',  # 697 + 1209 = 1906 (key 1)
    '2033': '2',  # 697 + 1336 = 2033 (key 2)
    '2174': '3',  # 697 + 1477 = 2174 (key 3)
    '1979': '4',  # 770 + 1209 = 1979 (key 4)
    '2106': '5',  # 770 + 1336 = 2106 (key 5)
    '2247': '6',  # 770 + 1477 = 2247 (key 6)
    '2061': '7',  # 852 + 1209 = 2061 (key 7)
    '2188': '8',  # 852 + 1336 = 2188 (key 8)
    '2329': '9',  # 852 + 1477 = 2329 (key 9)
    '2150': '*',  # 941 + 1209 = 2150 (key *)
    '2277': '0',  # 941 + 1336 = 2277 (key 0)
    '2418': '#'   # 941 + 1477 = 2418 (key #)
}
```

2. We observed that the code `2418` (representing the `#` key) was being used as a separator in the file.

3. We parsed the file to extract chunks of codes separated by `2418`, and for each chunk:
   - Extracted the unique 4-digit code
   - Mapped it to a keypad digit
   - Counted how many consecutive times it appeared (representing multiple key presses)

4. Using the multi-tap text entry system with the standard phone keypad layout, we decoded the message:
```python
t9_mapping = {
    '1': '1',
    '2': 'ABC',
    '3': 'DEF',
    '4': 'GHI',
    '5': 'JKL',
    '6': 'MNO',
    '7': 'PQRS',
    '8': 'TUV',
    '9': 'WXYZ',
    '0': ' ',
    '*': '*',
    '#': '#'
}
```

## The Message

The decoded message was: 
```
ONLYNINETIESKIDSWILLREMEMBERTHIS
```

When properly spaced:
```
ONLY NINETIES KIDS WILL REMEMBER THIS
```

This is a fitting message given that DTMF tones and multi-tap text entry were common technologies in the 1990s, which many people who grew up in that decade would recognize.

## Flag
The flag is:
```
DUCTF{ONLYNINETIESKIDSWILLREMEMBERTHIS}
```

## Key Insights
1. Recognizing DTMF from the challenge name
2. Understanding that the numbers represented sums of DTMF frequency pairs
3. Identifying the `2418` code as a separator
4. Applying multi-tap text entry decoding to the sequence of phone keypad digits

## Code
```python
import collections

# Map DTMF frequency sums to phone keypad digits
CODE_TO_KEY = {
    '1906': '1',  # 697 + 1209 = 1906 (key 1)
    '2033': '2',  # 697 + 1336 = 2033 (key 2)
    '2174': '3',  # 697 + 1477 = 2174 (key 3)
    '1979': '4',  # 770 + 1209 = 1979 (key 4)
    '2106': '5',  # 770 + 1336 = 2106 (key 5)
    '2247': '6',  # 770 + 1477 = 2247 (key 6)
    '2061': '7',  # 852 + 1209 = 2061 (key 7)
    '2188': '8',  # 852 + 1336 = 2188 (key 8)
    '2329': '9',  # 852 + 1477 = 2329 (key 9)
    '2150': '*',  # 941 + 1209 = 2150 (key *)
    '2277': '0',  # 941 + 1336 = 2277 (key 0)
    '2418': '#'   # 941 + 1477 = 2418 (key #)
}

def decode_dtmf(file_path):
    with open(file_path, 'r') as f:
        content = f.read().strip()

    # Split by the separator '2418' (which corresponds to the # key)
    chunks = content.split('2418')
    
    # Map each chunk to a key and its count
    key_sequences = []
    for chunk in chunks:
        if not chunk:
            continue
        codes = [chunk[i:i+4] for i in range(0, len(chunk), 4)]
        unique_codes = set(codes)
        if len(unique_codes) == 1:
            code = list(unique_codes)[0]
            key = CODE_TO_KEY.get(code)
            if key:
                count = len(codes)  # Number of consecutive key presses
                key_sequences.append((key, count))
    
    # Multi-tap text entry
    t9_mapping = {
        '1': '1',
        '2': 'ABC',
        '3': 'DEF',
        '4': 'GHI',
        '5': 'JKL',
        '6': 'MNO',
        '7': 'PQRS',
        '8': 'TUV',
        '9': 'WXYZ',
        '0': ' ',
        '*': '*',
        '#': '#'
    }
    
    message_t9 = []
    for key, count in key_sequences:
        if key in t9_mapping:
            letters = t9_mapping[key]
            if count > len(letters):
                message_t9.append(key)
            else:
                letter_index = (count - 1) % len(letters)
                message_t9.append(letters[letter_index])
    
    return "".join(message_t9)

# Decode the message
file_path = 'dtmf.txt'
message = decode_dtmf(file_path)
print(f"DUCTF{{{message}}}")
```
