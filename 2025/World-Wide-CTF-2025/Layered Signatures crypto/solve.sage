# solve.sage

# --- Parameters from the server ---
p = 157177458027947738464608587718505170872557537311336022386936190418737852141444802600222526305430833558655717806361264485789209743716195302937247478034883845835496282499162731072456548430299962306072692670825782721923481661135742935447793446928303177027490662275563294516442565718398572361235897805000082380599
q = x
gs_val = y
sm = z
leak = t
g_val = 25

# We can get x, y, z, t by nc chal.wwctf.com 8001

from hashlib import sha256
from Crypto.Util.number import long_to_bytes, bytes_to_long

def nxt(m):
    return bytes_to_long(sha256(long_to_bytes(int(m))).digest())

# --- Setup SageMath Rings and Fields ---
Fp = GF(p)
g = Fp(g_val)
gs = Fp(gs_val)
Z_p_minus_1 = Zmod(p - 1)

# --- 1. Recover the Private Key `s` ---
a_msg = sm[2]
s = Z_p_minus_1(-a_msg)
print(f"✅ Private key `s` recovered!")

# Verify that our recovered key `s` corresponds to the public key `gs`
assert g^s == gs, "Verification of recovered key failed!"
print(f"✅ Key verification successful!")

# --- 2. Forge a Signature for the Flag ---
m_mod_q = leak

# Use the same "random" values as the Python script for a direct conversion
b_f = 42
r_f = 1337
k_schnorr = 12345

# Calculate the challenge chain `cc_f`
cc_f = [nxt(m_mod_q)]
for _ in range(3):
    cc_f.append(nxt(cc_f[-1]))

# Calculate `sta_f`
# We use int() to work with standard Python integers for compatibility
sum_term = int(sum([g^b_f * Fp(c) for c in cc_f]))
sta_f = (m_mod_q - (sum_term % q)) % q

# Construct the forged `a_f` using the original formula
# We cast s back to a Python integer for this large calculation
s_int = int(s)
a_f = (p - 1 - s_int) * p - (q * r_f + sta_f) * (p - 1)

# Generate the 'weird_schnorr' signature for `a_f`
r_schnorr_val = g^k_schnorr
e_schnorr_bytes = sha256(long_to_bytes(int(r_schnorr_val)) + long_to_bytes(int(a_f))).digest()
e_schnorr = bytes_to_long(e_schnorr_bytes)
s_schnorr = (k_schnorr + s_int * e_schnorr) % ((p - 1) // 2)

# Assemble the final signature payload
final_sig = [s_schnorr, e_schnorr, a_f, b_f, b_f, b_f, b_f]
signature_str = ",".join(map(str, final_sig))

print("\n🚀 Forged signature payload:")
print(signature_str)