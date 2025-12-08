import asyncio
from app.services.xandeum_client import XandeumPRPCClient

async def test_connection():
    print("Testing Xandeum connection...")
    
    # Test testnet
    print("\n1. Testing Testnet...")
    client = XandeumPRPCClient(network="testnet")
    pnodes = await client.get_pnodes()
    print(f"   Got {len(pnodes)} pNodes from testnet")
    
    # Test mainnet
    print("\n2. Testing Mainnet...")
    client = XandeumPRPCClient(network="mainnet")
    pnodes = await client.get_pnodes()
    print(f"   Got {len(pnodes)} pNodes from mainnet")
    
    # Test network info
    print("\n3. Testing Network Info...")
    info = await client.get_network_info()
    print(f"   Epoch: {info.get('epoch', 'N/A')}")
    print(f"   Slot: {info.get('slot', 'N/A')}")
    
    await client.close()
    print("\n? Test complete!")

if __name__ == "__main__":
    asyncio.run(test_connection())
