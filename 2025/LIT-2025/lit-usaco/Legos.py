import sys
from collections import Counter

input = sys.stdin.read
data = input().splitlines()

idx = 0
t = int(data[idx])
idx += 1

for _ in range(t):
    n = int(data[idx])
    idx += 1
    grid = []
    for i in range(n):
        grid.append(data[idx])
        idx += 1
    S = []
    for r in range(n):
        for c in range(n):
            if grid[r][c] == '1':
                S.append((r, c))
    m = len(S)
    if m == 0:
        print(0)
        continue
    T = [(c, -r) for r, c in S]
    count = Counter()
    for sr, sc in S:
        for tr, tc in T:
            dx = sr - tr
            dy = sc - tc
            count[(dx, dy)] += 1
    max_overlap = max(count.values())
    print(m - max_overlap)