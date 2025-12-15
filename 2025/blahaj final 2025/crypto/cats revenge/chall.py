import random
from math import gcd
from secrets import vals

p = 2**127-1

for i in range(5):
    print(f"[ {i+1} / 5 ]")
    s = random.choice(vals)
    print(f"ðŸ± = {s}")
    try:
        a = int(input("ðŸ˜¾ = "))
        b = int(input("ðŸ˜¿ = "))
        c = int(input("ðŸ™€ = "))
    except EOFError:
        exit(0)
    if not all(abs(i) > p for i in [a, b, c]):
        print("ðŸ˜¿ðŸ˜¿ðŸ˜¿")
        break
    if gcd(a, b) != 1 or gcd(b, c) != 1 or gcd(c, a) != 1:
        print("ðŸ˜¿ðŸ˜¿ðŸ˜¿")
        break
    numer = a**3 + 3*a**2*b + 2*a*b**2 + b**3 + 2*a**2*c + 6*a*b*c + 3*b**2*c + 3*a*c**2 + 2*b*c**2 + c**3
    denom = a**2*b + a*b**2 + a**2*c + 2*a*b*c + b**2*c + a*c**2 + b*c**2
    if numer - s*denom:
        print("ðŸ˜¿ðŸ˜¿ðŸ˜¿")
        break
    print("ðŸ˜¸ðŸ˜¸ðŸ˜¸\n")
else:
    print("ðŸ˜½ðŸ˜½ðŸ˜½")
    print("blahaj{REDACTED}")