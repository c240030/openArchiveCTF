import math

# Given values from the challenge
n = 144984891276196734965453594256209014778963203195049670355310962211566848427398797530783430323749867255090629853380209396636638745366963860490911853783867871911069083374020499249275237733775351499948258100804272648855792462742236340233585752087494417128391287812954224836118997290379527266500377253541233541409
c = 120266872496180344790010286239079096230140095285248849852750641721628852518691698502144313546787272303406150072162647947041382841125823152331376276591975923978272581846998438986804573581487790011219372437422499974314459242841101560412534631063203123729213333507900106440128936135803619578547409588712629485231
hint = 867001369103284883200353678854849752814597815663813166812753132472401652940053476516493313874282097709359168310718974981469532463276979975446490353988
e = 65537

# Helper function to check for perfect squares efficiently
def is_perfect_square(n):
    if n < 0:
        return False, 0
    x = math.isqrt(n)
    if x * x == n:
        return True, x
    return False, 0

# 1. Approximate phi to get a guess for k
# phi = n - (p+q) + 1. Since p, q are ~sqrt(n), p+q is ~2*sqrt(n)
root_n = math.isqrt(n)
phi_guess = n - 2 * root_n + 1

# k is the unknown upper bits of phi. phi = k * 2^500 + hint
# So, k = (phi - hint) / 2^500
k_guess = phi_guess >> 500

# 2. Search for the correct k around our guess
# The approximation is very good, so k will be very close to k_guess.
search_range = 2000 # Search a small range around the guess
found = False

for i in range(search_range):
    # Check k_guess - i and k_guess + i
    for sign in [-1, 1]:
        if i == 0 and sign == 1: continue # Avoid checking k_guess twice

        k_cand = k_guess + (i * sign)

        # 3. Calculate s = p+q from k and check if it's valid
        # s = n - phi + 1 = n - (k * 2**500 + hint) + 1
        s_cand = (n - hint + 1) - k_cand * (2**500)

        # 4. Check if the discriminant (s^2 - 4n) is a perfect square
        delta_sq = s_cand * s_cand - 4 * n
        is_sq, delta = is_perfect_square(delta_sq)

        if is_sq:
            # 5. If it is, we have found p and q
            p = (s_cand + delta) // 2
            q = (s_cand - delta) // 2

            # Sanity check
            if p * q == n:
                print(f"[*] Found factors with k = {k_cand}")
                print(f"p = {p}")
                print(f"q = {q}")

                # 6. Decrypt the message
                phi = (p - 1) * (q - 1)
                d = pow(e, -1, phi)
                m = pow(c, d, n)

                # Convert message from long to bytes
                flag_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
                flag = flag_bytes.decode('utf-8')

                print("\n" + "="*40)
                print(f"Flag: {flag}")
                print("="*40)

                found = True
                break
    if found:
        break

if not found:
    print("\n[!] Failed to find factors within the search range.")
    print("[!] Try increasing the search_range.")