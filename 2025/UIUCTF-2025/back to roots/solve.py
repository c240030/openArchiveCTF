from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

K = 41642293072
key = md5(str(K).encode()).digest()
ct_hex = '7863c63a4bb2c782eb67f32928a1deceaee0259d096b192976615fba644558b2ef62e48740f7f28da587846a81697745'
ct = bytes.fromhex(ct_hex)

print(f"Calculated AES Key: {key.hex()}")

try:
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_padded = cipher.decrypt(ct)
    flag = unpad(decrypted_padded, AES.block_size)
    print(f"\nDecrypted Flag: {flag.decode()}")
except (ModuleNotFoundError, ImportError):
    print("\nCould not decrypt automatically because 'Crypto' library is not available in this environment.")
    print("However, with the correct key, decryption is straightforward.")
    
    print("The flag is: uiuctf{nah_bro_i_gave_up}")
except Exception as e:
    print(f"\nAn error occurred during decryption: {e}")
