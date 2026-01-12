import angr
import claripy

project = angr.Project('./checker', auto_load_libs=False)

flag_chars = [claripy.BVS(f'flag_{i}', 8) for i in range(42)]
flag = claripy.Concat(*flag_chars + [claripy.BVV(b'\n')])

state = project.factory.entry_state(stdin=flag)

for char in flag_chars:
    state.add_constraints(char >= 0x20)
    state.add_constraints(char <= 0x7e)
    state.add_constraints(char != ord('\n'))

sm = project.factory.simulation_manager(state)

print("[*] Searching for the flag, please wait (this might take a few minutes)...")

sm.explore(find=lambda s: b"Yes" in s.posix.dumps(1), 
           avoid=lambda s: b"No" in s.posix.dumps(1))

if sm.found:
    solution = sm.found[0].posix.dumps(0)
    print(f"\n[+] FLAG FOUND: {solution.decode().strip()}")
else:
    print("\n[-] Flag not found. Please recheck the success/failure addresses.")