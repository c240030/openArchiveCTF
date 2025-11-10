from pathlib import Path

# --- Configuration ---
# The directory to search. "." means the current directory.
TARGET_DIR = Path(".")
# The flag format we're looking for.
FLAG_PREFIX = b'brunner{'


# --- Script Logic ---
print("Starting search for the flag...")

found_flag = False
# Loop through every item in the current directory
for file_path in TARGET_DIR.glob("*"):
    # Check if it's a file and not our script itself
    if file_path.is_file() and file_path.name != "find_flag.py":
        try:
            # Open the file in binary mode to read raw bytes
            with open(file_path, "rb") as f:
                content = f.read()
                
                # Check if the flag prefix exists in the content
                if FLAG_PREFIX in content:
                    print(f"\n[SUCCESS] Found a potential flag in: '{file_path.name}'")
                    
                    # Try to extract the full flag from the prefix to the closing brace '}'
                    start_index = content.find(FLAG_PREFIX)
                    end_index = content.find(b'}', start_index)
                    
                    if end_index != -1:
                        # Decode the byte string into a readable text string
                        flag = content[start_index : end_index + 1].decode()
                        print(f"    --> Flag: {flag}")
                        found_flag = True
                        break # Stop searching once the flag is found
                    else:
                        print(f"    --> Found prefix but couldn't find closing brace '}}'.")

        except Exception as e:
            # This handles any errors with reading files, like permission issues
            print(f"[!] Could not read file '{file_path.name}': {e}")

if not found_flag:
    print("\nSearch complete. No flag was found.")
else:
    print("\nSearch complete!")
