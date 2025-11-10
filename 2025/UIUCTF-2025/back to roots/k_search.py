from decimal import Decimal, getcontext
from hashlib import md5

# Set high precision for calculations
getcontext().prec = 100

# The leaked fractional part
L = Decimal('4336282047950153046404')
f_leak = L / Decimal('1e22')

# The correct key hash provided by the user
correct_key_hash = '6bad796b3bd807878a18c580efa36a04'

# Range for the integer part of the square root
I_min = 100000
I_max = 316228

found_K = None

print("Searching for the correct K...")
for i in range(I_min, I_max + 1):
    I_dec = Decimal(i)
    
    # Construct the approximate square root
    s_approx = I_dec + f_leak
    
    # The best candidate for K is the square of s_approx, rounded to the nearest integer
    K_candidate = int(s_approx**2)
    
    # We might be off by one due to rounding, so check K_candidate and K_candidate + 1
    for k_test in [K_candidate, K_candidate + 1]:
        # Hash the candidate and check against the correct key
        key_hash_candidate = md5(str(k_test).encode()).hexdigest()
        
        if key_hash_candidate == correct_key_hash:
            found_K = k_test
            print(f"Success! Found matching K.")
            break
    if found_K:
        break

if found_K:
    print(f"\nThe correct secret number K is: {found_K}")
    
    # Final verification step with the correct K
    getcontext().prec = 28 # Match the challenge environment
    s_verify = Decimal(found_K).sqrt()
    print(f"sqrt(K) with precision 28: {s_verify}")
    leak_calculated = int(str(s_verify).split('.')[-1])
    print(f"Calculated leak from this K: {leak_calculated}")
    print(f"Original leak from challenge: {L}")
    if int(L) == leak_calculated:
        print("Verification successful: This K also produces the correct leak.")
    else:
        print("Verification discrepancy: This K produces a different leak. This is unexpected.")
else:
    print("Search failed. Could not find a K that matches the given key.")
