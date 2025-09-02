from pytoniq_core.crypto.keys import mnemonic_to_private_key
from tonutils.client import ToncenterClient
from tonutils.wallet import WalletV2R2, WalletV3R1, WalletV4R2, WalletV5R1
import asyncio
import aiohttp
import json
import sys

TONCENTER_API_KEYS = {
    "mainnet": "6548......436",
    "testnet": "2879a....b6df",
}

async def get_balance(address, network):
    url = f"https://{'testnet.' if network == 'testnet' else ''}toncenter.com/api/v2/getAddressInformation"
    params = {"address": address}
    headers = {"X-API-Key": TONCENTER_API_KEYS[network]}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            if data.get("ok"):
                return int(data["result"]["balance"])
            return 0

def save_to_json(data):
    try:
        with open('wallet_balance.json', 'r') as f:
            existing_data = json.load(f)
    except:
        existing_data = []
    
    existing_data.append(data)
    
    with open('wallet_balance.json', 'w') as f:
        json.dump(existing_data, f, indent=2)

async def check_wallet_balance(mnemonic_phrase, network="mainnet"):
    try:
        private_key = mnemonic_to_private_key(mnemonic_phrase.split())[1]
        client = ToncenterClient(api_key=TONCENTER_API_KEYS[network], is_testnet=(network == "testnet"))
        
        wallets = [
            ("v2", WalletV2R2.from_private_key(client, private_key)),
            ("v3", WalletV3R1.from_private_key(client, private_key)),
            ("v4r2", WalletV4R2.from_private_key(client, private_key)),
            ("v5", WalletV5R1.from_private_key(client, private_key)),
        ]
        
        results = []
        
        for version, wallet in wallets:
            address = wallet.address.to_str()
            balance_nano = await get_balance(address, network)
            balance_ton = balance_nano / 1e9
            
            result = {
                "address": address,
                "version": version,
                "balance": balance_ton,
                "mnemonic": mnemonic_phrase
            }
            
            results.append(result)
            
            if balance_ton > 0:
                save_to_json(result)
        
        return results
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No mnemonic provided"}))
        sys.exit(1)
    
    mnemonic = sys.argv[1]
    network = sys.argv[2] if len(sys.argv) > 2 else "mainnet"
    
    result = asyncio.run(check_wallet_balance(mnemonic, network))
    print(json.dumps(result))
