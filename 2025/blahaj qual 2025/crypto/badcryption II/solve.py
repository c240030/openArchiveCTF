import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sympy.ntheory.modular import crt

p = 49278241238643848738524823448834114960140393694771426989126687
g = 5
A = 10800503958313532508703483527316858486221753413274690920762040 # client_public_key
B = 1408737133570836687938369313016555892179945972238420904039351 # server_public_key
iv_hex = "27899e4a13288b70c146368509f07b03"
encrypted_msg_b64 = "oDdTRGeG7vChufQ1k9vK7CSDhcTASt0z0QIoprH04Kw="

factors = [2, 15619, 17419, 29671, 39323, 53327, 69193, 72727, 75181, 76333, 80761, 81343, 82619, 92863]

def solve_dlp():
    prod = 1
    for f in factors:
        prod *= f
    
    if prod != p - 1:
        print(f"Warning: Product of factors {prod} does not match p-1 {p-1}")
        if (p-1) % prod == 0:
            rem = (p-1) // prod
            print(f"Missing factor product: {rem}")
            if rem > 1:
                factors.append(rem)
        else:
            print("Factors do not divide p-1 cleanly!")
            return None
    
    remainders = []
    moduli = []

    for q in factors:
        
        exp = (p - 1) // q
        g_prime = pow(g, exp, p)
        h_prime = pow(A, exp, p)
        
        found = False
        for i in range(q):
            if pow(g_prime, i, p) == h_prime:
                remainders.append(i)
                moduli.append(q)
                found = True
                break
        
        if not found:
            print(f"Could not find log for factor {q}")
            return None

    x, _ = crt(moduli, remainders)
    return x

def decrypt():
    private_key = solve_dlp()
    print(f"Found private key: {private_key}")
    
    if pow(g, private_key, p) != A:
        print("Error: Private key does not match public key A")
        return

    shared_secret = pow(B, private_key, p)
    print(f"Shared secret: {shared_secret}")
    
    shared_secret_str = str(shared_secret)
    key = hashlib.sha256(shared_secret_str.encode('utf-8')).digest()
    
    iv = bytes.fromhex(iv_hex)
    ciphertext = base64.b64decode(encrypted_msg_b64)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        print(f"Decrypted message: {plaintext.decode('utf-8')}")
    except Exception as e:
        print(f"Decryption failed: {e}")

if __name__ == "__main__":
    decrypt()
