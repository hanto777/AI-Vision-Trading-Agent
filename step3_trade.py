import os
from dotenv import load_dotenv
from web3 import Web3

# Загружаем ключи из .env файла
load_dotenv()

# 1. Network & Wallet setup
RPC_URL = "https://rpc.mantle.xyz"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
account = web3.eth.account.from_key(PRIVATE_KEY)
wallet_address = account.address


# 2. Wrapped MNT Contract on Mantle
WMNT_ADDRESS = web3.to_checksum_address("0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8")

# 3. Minimal ABI for deposit()
WMNT_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    }
]

wmnt_contract = web3.eth.contract(address=WMNT_ADDRESS, abi=WMNT_ABI)

def execute_wrap():
    print("=== 🎁 ON-CHAIN EXECUTION: WRAP MNT ===")
    
    amount_in_mnt = 0.1
    amount_in_wei = web3.to_wei(amount_in_mnt, 'ether')
    
    print(f"Initiating transfer of {amount_in_mnt} MNT to WMNT smart contract...")
    
    try:
        nonce = web3.eth.get_transaction_count(wallet_address)
        
        # Build transaction
        tx = wmnt_contract.functions.deposit().build_transaction({
            'from': wallet_address,
            'value': amount_in_wei,
            'gas': 100000, 
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })
        
        print("✍️ Signing transaction locally...")
        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        
        print("📡 Broadcasting to Mantle network...")
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print("✅ SUCCESS! Transaction confirmed.")
        print(f"🔗 Explorer: https://explorer.mantle.xyz/tx/{web3.to_hex(tx_hash)}")
        
    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")

if __name__ == "__main__":
    execute_wrap()