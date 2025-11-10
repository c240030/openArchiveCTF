# Import necessary Sage and Python libraries
from sage.all import *
from Crypto.Util.number import long_to_bytes

# --- Given Problem Parameters ---
p = 3059506932006842768669313045979965122802573567548630439761719809964279577239571933
a_int = 2448848303492708630919982332575904911263442803797664768836842024937962142592572096
Gx_int = 3
Qx_int = 1461547606525901279892022258912247705593987307619875233742411837094451720970084133

# --- Final Solution ---

# 1. Setup the finite field and get both possible x0 roots.
F = GF(p)
a = F(a_int)
Gx = F(Gx_int)
Qx = F(Qx_int)

x0_sq = -a / 3
if not x0_sq.is_square():
    raise ValueError("Cannot find singular point. Check parameters.")

x0_roots = [x0_sq.sqrt(), -x0_sq.sqrt()]
print("[*] Found two potential x0 roots. Testing all four final possibilities...")

# 2. Iterate through each possible x0 root.
for i, x0 in enumerate(x0_roots):
    print(f"\n--- Testing case with x0 root #{i+1} ({x0}) ---")
    try:
        # Recover parameters based on the current x0
        b = 2 * x0^3
        
        # The tangent slope m = sqrt(3*x0) must exist
        m_sq = 3*x0
        if not m_sq.is_square():
            print("    - Invalid case: m = sqrt(3*x0) does not exist.")
            continue
        m = m_sq.sqrt()
        
        # The y-coordinates for G and Q must exist
        Gy_sq = Gx^3 + a*Gx + b
        Qy_sq = Qx^3 + a*Qx + b
        if not Gy_sq.is_square() or not Qy_sq.is_square():
            print("    - Invalid case: G or Q is not on the curve for this x0.")
            continue
        
        Gy = Gy_sq.sqrt()
        Qy = Qy_sq.sqrt()
        print(f"    - Valid parameters found. G=({Gx},{Gy}), Q=({Qx},{Qy})")

        # Apply the isomorphism
        alpha = (Gy - m*(Gx-x0)) / (Gy + m*(Gx-x0))
        beta = (Qy - m*(Qx-x0)) / (Qy + m*(Qx-x0))
        
        # Solve DLP for both flag possibilities for this case
        flag_int_1 = discrete_log(beta, alpha)
        flag_int_2 = discrete_log(beta.inverse(), alpha)
        
        # Attempt to decode both integers
        try:
            flag_bytes = long_to_bytes(int(flag_int_1))
            print(f"\n[+] SUCCESS! Flag found: {flag_bytes.decode('utf-8')}")
            exit() # Stop the script once the flag is found
        except (UnicodeDecodeError, ValueError):
            print(f"    - Possibility 1 failed to decode.")
        
        try:
            flag_bytes = long_to_bytes(int(flag_int_2))
            print(f"\n[+] SUCCESS! Flag found: {flag_bytes.decode('utf-8')}")
            exit() # Stop the script once the flag is found
        except (UnicodeDecodeError, ValueError):
            print(f"    - Possibility 2 failed to decode.")

    except Exception as e:
        print(f"    - An unexpected error occurred: {e}")

print("\n[!] All possibilities exhausted and no valid flag was found.")