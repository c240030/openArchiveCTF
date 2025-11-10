import math
from gmpy2 import iroot, is_prime, next_prime, prev_prime
from Crypto.Util.number import long_to_bytes

# --- IMPORTANT: Paste your new N and ct from the challenge here ---
N = 34546497157207880069779144631831207265231460152307441189118439470134817451040294541962595051467936974790601780839436065863454184794926578999811185968827621504669046850175311261350438632559611677118618395111752688984295293397503841637367784035822653287838715174342087466343269494566788538464938933299114092019991832564114273938460700654437085781899023664719672163757553413657400329448277666114244272477880443449956274432819386599220473627937756892769036756739782458027074917177880632030971535617166334834428052274726261358463237730801653954955468059535321422372540832976374412080012294606011959366354423175476529937084540290714443009720519542526593306377
ct = 32130352215164271133656346574994403191937804418876038099987899285740425918388836116548661879290345302496993945260385667068119439335225069147290926613613587179935141225832632053477195949276266017803704033127818390923119631817988517430076207710598936487746774260037498876812355794218544860496013734298330171440331211616461602762715807324092281416443801588831683678783343566735253424635251726943301306358608040892601269751843002396424155187122218294625157913902839943220894690617817051114073999655942113004066418001260441287880247349603218620539692362737971711719433735307458772641705989685797383263412327068222383880346012169152962953918108171850055943194
e = 65537

p_found = 0
num_primes = 0

# The number of factors is likely around 16. Let's try 16, 17, and 15.
for k in [16, 17, 15]:
    print(f"\n[*] Trying with {k} prime factors...")
    p_approx, _ = iroot(N, k)
    
    # Start searching from an odd number near the approximation
    p_candidate = p_approx if p_approx % 2 != 0 else p_approx - 1
    
    # Increased search range to handle larger prime gaps
    print(f"[*] Searching near approximation: {p_candidate}")
    for offset in range(5_000_000): # Larger search range: 5 million
        # Check below the approximation
        p_down = p_candidate - (2 * offset)
        if is_prime(p_down) and N % p_down == 0:
            p_found = p_down
            break
        
        # Check above the approximation
        p_up = p_candidate + (2 * offset)
        if is_prime(p_up) and N % p_up == 0:
            p_found = p_up
            break
            
    if p_found:
        num_primes = k
        break

if not p_found:
    raise ValueError("Factorization failed. The primes might be further from the k-th root approximation than expected.")

print(f"[+] Found a prime factor with k={num_primes}: {p_found}")

# Find all other consecutive prime factors
factors = [p_found]
temp_N = N // p_found

# Search forwards (next_prime)
p_current = p_found
while temp_N > 1:
    p_next = next_prime(p_current)
    if temp_N % p_next == 0:
        factors.append(p_next)
        temp_N //= p_next
        p_current = p_next
    else:
        break

# Search backwards (prev_prime)
p_current = p_found
while temp_N > 1:
    p_prev = prev_prime(p_current)
    if temp_N % p_prev == 0:
        factors.append(p_prev)
        temp_N //= p_prev
        p_current = p_prev
    else:
        break
        
assert temp_N == 1, "Failed to fully factorize N"
assert len(factors) == num_primes, f"Found an incorrect number of factors: {len(factors)}, expected {num_primes}"
print(f"[+] Successfully factored N into {len(factors)} primes.")

# Calculate phi(N) and decrypt
phi_N = 1
for p in factors:
    phi_N *= (p - 1)

d = pow(e, -1, phi_N)
pt_long = pow(ct, d, N)
flag = long_to_bytes(pt_long)

print("\n[+] 🚩 The flag is:")
print(flag.decode())