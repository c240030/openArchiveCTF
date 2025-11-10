from collections import deque

def solve():
    n, m = map(int, input().split())
    
    elevation = []
    for i in range(n):
        elevation.append(list(map(int, input().split())))
    
    a = int(input())
    attractions = set()
    for _ in range(a):
        r, c = map(int, input().split())
        attractions.add((r-1, c-1))
    
    q = int(input())
    
    queries = []
    unique_capacities = set()
    for i in range(q):
        capacity, target = map(int, input().split())
        queries.append((capacity, target, i))
        unique_capacities.add(capacity)
    
    # Precompute for each unique capacity
    results = [None] * q
    
    for capacity in unique_capacities:
        # Find best starting position for each possible target
        best_for_target = {}
        
        # Track which cells we've already processed for this capacity
        processed = set()
        
        for r in range(n):
            for c in range(m):
                if (r, c) in processed or elevation[r][c] > capacity:
                    continue
                
                # BFS to find component size and mark all cells in component
                visited = set()
                queue = deque([(r, c)])
                visited.add((r, c))
                component_cells = [(r, c)]
                attraction_count = 1 if (r, c) in attractions else 0
                
                while queue:
                    cr, cc = queue.popleft()
                    curr_elev = elevation[cr][cc]
                    
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        
                        if (0 <= nr < n and 0 <= nc < m and 
                            (nr, nc) not in visited and
                            elevation[nr][nc] <= capacity and
                            abs(elevation[nr][nc] - curr_elev) <= 1):
                            
                            visited.add((nr, nc))
                            queue.append((nr, nc))
                            component_cells.append((nr, nc))
                            
                            if (nr, nc) in attractions:
                                attraction_count += 1
                
                # Mark all cells in this component as processed
                processed.update(component_cells)
                
                # Find lexicographically smallest cell in this component
                component_cells.sort()
                min_r, min_c = component_cells[0]
                
                # Update best positions for all targets this component can satisfy
                for target in range(1, attraction_count + 1):
                    if target not in best_for_target:
                        best_for_target[target] = (min_r + 1, min_c + 1)
        
        # Answer all queries for this capacity
        for i, (cap, target, orig_idx) in enumerate(queries):
            if cap == capacity:
                if target in best_for_target:
                    results[orig_idx] = best_for_target[target]
                else:
                    results[orig_idx] = (-1, -1)
    
    # Output results in original order
    for result in results:
        print(result[0], result[1])

solve()