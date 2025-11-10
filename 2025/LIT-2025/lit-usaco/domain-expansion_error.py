MOD = 10**9 + 7

n = int(input())
target = tuple(map(int, input().split()))

# Use iterative approach to count ways
# ways[state] = number of ways to reach that state
ways = {(0,): 1}

# Process by increasing array length to avoid deep recursion
for current_length in range(1, n):
    next_ways = {}
    
    # Process all states of current length
    for state in ways:
        if len(state) != current_length:
            continue
            
        state_ways = ways[state]
        
        # Try expanding each element
        for i in range(len(state)):
            new_val = state[i] + 1
            
            # Try inserting to the left
            if current_length + 1 <= n:
                new_state = state[:i] + (new_val,) + state[i:]
                next_ways[new_state] = (next_ways.get(new_state, 0) + state_ways) % MOD
            
            # Try inserting to the right
            if current_length + 1 <= n:
                new_state = state[:i+1] + (new_val,) + state[i+1:]
                next_ways[new_state] = (next_ways.get(new_state, 0) + state_ways) % MOD
    
    # Add new states to ways
    ways.update(next_ways)

# Output result
print(ways.get(target, 0))