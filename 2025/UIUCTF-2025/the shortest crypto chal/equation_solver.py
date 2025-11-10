def solve_diophantine_equation():
    """
    Finds integer solutions to a**4 + b**4 == c**4 + d**4 + 17
    using a meet-in-the-middle approach.
    """
    limit = 2000# A sufficiently large search limit# 1. Pre-compute values for the right-hand side (c, d)print(f"Starting pre-computation with limit = {limit}...")
    sums_of_powers = {}
    for c in range(1, limit):
        for d in range(1, c + 1):# Assume c >= d to reduce redundant calcs
            val = c**4 + d**4 + 17
            sums_of_powers[val] = (c, d)
    print("Pre-computation finished.")

# 2. Search for (a, b) and check against the pre-computed mapprint("Starting search phase...")
    for a in range(1, limit):
        for b in range(1, a + 1):# Assume a >= b
            target = a**4 + b**4
            if target in sums_of_powers:
                c, d = sums_of_powers[target]

# Found a valid set of integers!
                solution_set = tuple(sorted((a, b, c, d)))
                print(f"Found integer solution set (a,b,c,d): {solution_set}")

# Calculate the key for the crypto part
                product = a * b * c * d
                key = str(product).zfill(16)
                print(f"Derived AES Key: {key}")
                return

solve_diophantine_equation()