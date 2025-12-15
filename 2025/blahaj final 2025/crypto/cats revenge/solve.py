from pwn import *
from fractions import Fraction
import math

# --- Math Helpers ---

def lcm(a, b):
    if a == 0 or b == 0: return 0
    return abs(a * b) // math.gcd(a, b)

def gcd3(a, b, c):
    return math.gcd(a, math.gcd(b, c))

def is_square(n):
    if n < 0: return False
    if n == 0: return True
    root = math.isqrt(n)
    return root * root == n

def find_seed(s):
    """
    Finds a rational point (u, v) satisfying u*v^2 + (u^2 - s*u)*v + 1 = 0.
    This corresponds to the transformed equation u + v + 1/(uv) = s.
    """
    limit_d = 400
    limit_n = 1000
    
    for d in range(1, limit_d):
        for n in range(-limit_n, limit_n):
            if n == 0: continue
            
            # We treat the equation as quadratic in v.
            # Discriminant D = (u^2 - su)^2 - 4u must be a square in rationals.
            # Substituting u = n/d, we check if the numerator of D is a square integer.
            term = (n**2 - s*n*d)**2 - 4*n*(d**3)
            
            if is_square(term):
                y_val = math.isqrt(term)
                
                # Quadratic formula: v = ( -(u^2 - su) +/- sqrt(D) ) / 2u
                # Simplifies to: v = (-n^2 + snd +/- y_val) / (2nd)
                v_num = -n**2 + s*n*d + y_val
                v_den = 2 * n * d
                
                return Fraction(n, d), Fraction(v_num, v_den)
    return None

def next_point(U, V, s):
    """
    Computes the next point on the cubic curve using the tangent doubling method.
    """
    # F(u, v) = u*v^2 + u^2*v - s*u*v + 1
    # Partial derivatives
    Fu = V**2 + 2*U*V - s*V
    Fv = 2*U*V + U**2 - s*U
    
    if Fv == 0: return None
    
    slope = -Fu / Fv
    
    # Coeff of u^3 in expansion of F(u, slope*u + C) is slope^2 + slope
    A = slope**2 + slope
    if A == 0: return None
    
    # Coeff of u^2 in expansion
    C = V - slope * U
    B = 2 * slope * C + C - s * slope
    
    # Sum of roots relation: u_new + 2*u_old = -B/A
    U_new = -B/A - 2*U
    V_new = slope * (U_new - U) + V
    
    return U_new, V_new

def solve():
    conn = remote("crypto-cats-revenge.finals.blahaj.sg", 28032)
    p_limit = 2**127
    
    for i in range(5):
        # 1. Parse target s
        # The prompt format is usually: [Round] \n ðŸ ± = {s}
        try:
            conn.recvuntil(b" = ")
            s_line = conn.recvline().strip().decode()
            if not s_line: # Retry if empty line received
                conn.recvuntil(b" = ")
                s_line = conn.recvline().strip().decode()
            s = int(s_line)
            print(f"[*] Round {i+1}/5: Target s = {s}")
        except ValueError as e:
            log.error(f"Parsing error: {e}. Received: {s_line}")
            conn.close()
            return

        # 2. Find seed
        seed = find_seed(s)
        if seed is None:
            log.error(f"Could not find seed for s={s}")
            conn.close()
            return
        
        U, V = seed
        
        # 3. Iterate to satisfy size constraints
        while True:
            # Map (u, v) back to integers (a, b, c)
            # Transformation derived from u=X/Y, v=Y/Z => X=uv, Y=v, Z=1
            X = U * V
            Y = V
            Z = Fraction(1, 1)
            
            # Convert fractions to integers by clearing denominators
            common_den = lcm(X.denominator, lcm(Y.denominator, Z.denominator))
            Xi = X.numerator * (common_den // X.denominator)
            Yi = Y.numerator * (common_den // Y.denominator)
            Zi = Z.numerator * (common_den // Z.denominator)
            
            # Substitution: X = a+b, Y = b+c, Z = c+a
            # Inverse: a = (X-Y+Z)/2, etc. (Since homogeneous, we can drop /2)
            a = Xi - Yi + Zi
            b = Xi + Yi - Zi
            c = -Xi + Yi + Zi
            
            # Simplify by GCD
            g = gcd3(a, b, c)
            a //= g
            b //= g
            c //= g
            
            # Check challenge constraints
            if abs(a) > p_limit and abs(b) > p_limit and abs(c) > p_limit:
                if math.gcd(a, b) == 1 and math.gcd(b, c) == 1 and math.gcd(c, a) == 1:
                    print(f"[+] Found valid solution. Sending...")
                    
                    # Send inputs consuming the prompts to keep buffer clean
                    conn.sendlineafter(b" = ", str(a).encode())
                    conn.sendlineafter(b" = ", str(b).encode())
                    conn.sendlineafter(b" = ", str(c).encode())
                    break
            
            # Generate next point
            res = next_point(U, V, s)
            if res is None:
                log.error("Tangent method hit singularity.")
                return
            U, V = res

    print("[*] All rounds complete. Flag incoming...")
    conn.interactive()

if __name__ == "__main__":
    solve()