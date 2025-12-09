def xor(*args):
    result = args[0]
    for arg in args[1:]:
        result = bytes(a ^ b for a, b in zip(result, arg))
    return result

iv = bytes.fromhex("a74286dc53a7e51a19de722b1e22a9bd")
pt = bytes.fromhex("03a4113b96b860e0fafd6a00c3583f1712c0ba08dd46547ddb87f3d61f838a323ea10466a8b86ef2ecd14642a5691935")
ct = bytes.fromhex("220c4c94a435fe05c4432802208cc612fb8fe3d29a75f089977c401b8f28c4d75fb9a2c30d1b99275e8188917c4d134e")

c0 = ct[:16]
c1 = ct[16:32]
c2 = ct[32:48]

p0_prime = pt[:16]
p1_prime = pt[16:32]
p2_prime = pt[32:48]

p0 = xor(p2_prime, c1, iv)
p1 = xor(p1_prime, c2, c0)
p2 = xor(p0_prime, iv, c1)

print(p0 + p1 + p2)
