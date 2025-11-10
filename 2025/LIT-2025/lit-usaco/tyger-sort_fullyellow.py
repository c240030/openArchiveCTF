from itertools import permutations

def tyger_sort(perm):
    """Simulate Tyger Sort algorithm exactly as described"""
    n = len(perm)
    p = perm[:]
    
    for x in range(n, 0, -1):  # x from n down to 1
        i = 1
        
        # Find position of x
        while p[i-1] != x:
            i += 1
        
        # Bubble x leftward while it's smaller than left neighbor
        while i > 1 and p[i-1] < p[i-2]:
            p[i-1], p[i-2] = p[i-2], p[i-1]
            i -= 1
    
    return p

def solve_case(target):
    """Find a permutation that gives target after Tyger Sort"""
    n = len(target)
    
    # Try all permutations (this works for the given constraints)
    for perm in permutations(range(1, n+1)):
        if tyger_sort(list(perm)) == target:
            return list(perm)
    
    return None

def main():
    t = int(input())
    
    for _ in range(t):
        n = int(input())
        target = list(map(int, input().split()))
        
        result = solve_case(target)
        
        if result is None:
            print(-1)
        else:
            print(*result)

if __name__ == "__main__":
    main()