import sys

input = sys.stdin.read
data = input().split()

index = 0
n = int(data[index])
index += 1

p = [0] * n
for i in range(n):
    p[i] = int(data[index])
    index += 1

pos = [0] * (n + 1)
for i in range(n):
    pos[p[i]] = i

q = int(data[index])
index += 1

for _ in range(q):
    x = int(data[index])
    y = int(data[index + 1])
    index += 2
    if x != y:
        px = pos[x]
        py = pos[y]
        p[px], p[py] = p[py], p[px]
        pos[x] = py
        pos[y] = px

print(' '.join(map(str, p)))