from pwn import *
import re
import collections

context.log_level = 'info'

def solve():
    host = "misc-rescripter.chals.blahaj.sg"
    port = 28447

    try:
        r = remote(host, port)
    except Exception as e:
        print(f"[!] Cannot connect: {e}")
        return

    print("[-] Receiving code from server...")
    
    try:
        data = r.recvuntil(b"Running the script...", timeout=10).decode()
        r.recvuntil(b"shimmy shimmy ya: ", timeout=2)
    except Exception as e:
        print(f"[!] Error receiving data: {e}")
        r.close()
        return

    print("[-] Code received. Analyzing...")

    main_search = re.search(r'def main\(\):([\s\S]+?)(?:if __name__|$)', data)
    if not main_search:
        print("[!] Cannot find main() function.")
        r.close()
        return

    start_match = re.search(r'funtime_(\d+)\s*\([^,]+,\s*(\d+)\)', main_search.group(1))
    if not start_match:
        print("[!] Cannot find starting function in main.")
        r.close()
        return

    start_node = int(start_match.group(1))
    start_weight = int(start_match.group(2))
    print(f"[-] Start at: funtime_{start_node}, Start weight: {start_weight}")

    func_blocks = re.split(r'def funtime_', data)
    
    adj = {}
    target_node = None
    target_weight = 0

    for block in func_blocks:
        header = re.match(r'^(\d+)\(p, w\):', block)
        if not header:
            continue
        
        node_id = int(header.group(1))
        
        if 'get_flag()' in block:
            target_node = node_id
            w_match = re.search(r'if w == (\d+):', block)
            if w_match:
                target_weight = int(w_match.group(1))
            continue 
        
        transitions = re.findall(r"d == '([UDLR])':\s+funtime_(\d+)\(r, w\s*\+\s*(\d+)\)", block)
        
        adj[node_id] = []
        for direction, next_node, cost in transitions:
            adj[node_id].append((direction, int(next_node), int(cost)))

    if target_node is None:
        print("[!] Cannot find target (get_flag).")
        r.close()
        return

    print(f"[-] Dest: funtime_{target_node}, Total weight: {target_weight}")

    queue = collections.deque([(start_node, start_weight, "")])
    
    visited = set() 
    solution = None

    while queue:
        u, w, path = queue.popleft()
        
        if u == target_node:
            if w == target_weight:
                solution = path
                break
            continue
        
        if w >= target_weight:
            continue
        if (u, w) in visited:
            continue
        visited.add((u, w))
        
        if u in adj:
            for direction, v, cost in adj[u]:
                queue.append((v, w + cost, path + direction))

    if solution:
        print(f"[+] Path found: {solution}")
        r.sendline(solution.encode())
        
        print("[-] Waiting for flag...")
        try:
            response = r.recvall(timeout=3).decode().strip()
            print("\n" + "="*40)
            print(response)
            print("="*40 + "\n")
        except:
            pass
    else:
        print("[!] No valid path found.")
        r.close()

if __name__ == '__main__':
    solve()
