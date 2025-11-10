import socket

# --- Connection Details ---
HOST = "ctfi.ng"
PORT = 31555
p = 2**255 - 19

def mod_inverse(a, m):
    """Calculates the modular multiplicative inverse of a modulo m."""
    return pow(a, m - 2, m)

def lagrange_interpolate_at_zero(points, m):
    """
    Calculates f(0) using Lagrange Interpolation.
    'points' is a list of tuples [(x1, y1), (x2, y2), ...].
    """
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    f_0 = 0
    for j in range(len(points)):
        numerator = 1
        denominator = 1
        for i in range(len(points)):
            if i == j:
                continue
            numerator = (numerator * (-x_coords[i])) % m
            denominator = (denominator * (x_coords[j] - x_coords[i])) % m
        
        lagrange_poly_at_0 = (numerator * mod_inverse(denominator, m)) % m
        f_0 = (f_0 + y_coords[j] * lagrange_poly_at_0) % m
        
    return f_0

# --- Connect and Solve ---
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    with s.makefile(mode='rw', encoding='utf-8') as f:
        welcome = f.readline().strip()
        print(f"Server: {welcome}")

        points_for_R = []
        for i in range(1, 8):
            print(f"Querying for x = {i} and x = {-i}...")
            
            f.write(str(i) + '\n')
            f.flush()
            y1 = int(f.readline().strip())
            
            f.write(str(p - i) + '\n')
            f.flush()
            y2 = int(f.readline().strip())
            
            y_R = pow(i, 2, p)
            numerator = (y1 - y2 + p) % p
            denominator_inv = mod_inverse((2 * i) % p, p)
            val_R = (numerator * denominator_inv) % p
            
            points_for_R.append((y_R, val_R))
            print(f"  -> Got point for R: ({y_R}, {val_R})")

        print("\nAll points gathered. Calculating the secret...")
        secret = lagrange_interpolate_at_zero(points_for_R, p)
        print(f"Calculated secret = {secret}")
        
        # --- THE FIX IS HERE ---
        # The server sends "secret? " with no newline. Read exactly 8 characters.
        prompt = f.read(8)
        print(f"Server: {prompt}")
        
        f.write(str(secret) + '\n')
        f.flush()
        print(f"Sent secret: {secret}")
        
        # The flag, however, is sent with a newline, so readline() is correct here.
        flag = f.readline().strip()
        print("\n--- FLAG ---")
        print(flag)