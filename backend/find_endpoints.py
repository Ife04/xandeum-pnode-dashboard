import aiohttp
import asyncio
import json

async def test_all_possible_endpoints():
    """Test all possible Xandeum RPC endpoint formats"""
    
    base_urls = [
        "https://mainnet.xandeum.network",
        "https://testnet.xandeum.network",
        "http://mainnet.xandeum.network",  # Try HTTP
        "http://testnet.xandeum.network",  # Try HTTP
    ]
    
    # Try different port combinations
    ports = ["", ":8899", ":80", ":443", ":8080"]
    
    # Try different path combinations
    paths = ["", "/", "/rpc", "/api", "/api/v1", "/v1/rpc"]
    
    methods = ["getClusterNodes", "getVoteAccounts", "getEpochInfo"]
    
    successful_endpoints = []
    
    for base in base_urls:
        for port in ports:
            for path in paths:
                endpoint = f"{base}{port}{path}"
                print(f"\n?? Testing: {endpoint}")
                
                for method in methods:
                    try:
                        async with aiohttp.ClientSession() as session:
                            payload = {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": method,
                                "params": []
                            }
                            
                            try:
                                async with session.post(
                                    endpoint,
                                    json=payload,
                                    timeout=aiohttp.ClientTimeout(total=3)
                                ) as response:
                                    if response.status == 200:
                                        data = await response.text()
                                        if "result" in data or '"error"' in data:
                                            print(f"  ? {method}: SUCCESS (200)")
                                            if endpoint not in successful_endpoints:
                                                successful_endpoints.append(endpoint)
                                                
                                            # Try to parse and show small sample
                                            try:
                                                json_data = json.loads(data)
                                                if "result" in json_data:
                                                    result = json_data["result"]
                                                    if isinstance(result, list):
                                                        print(f"     Found {len(result)} items")
                                                    elif isinstance(result, dict):
                                                        print(f"     Keys: {list(result.keys())[:3]}...")
                                            except:
                                                pass
                                        else:
                                            print(f"  ?? {method}: Got 200 but no JSON-RPC response")
                                    else:
                                        print(f"  ? {method}: HTTP {response.status}")
                            except Exception as e:
                                print(f"  ? {method}: Error - {str(e)[:50]}")
                                
                    except Exception as e:
                        print(f"  ? {method}: Failed - {str(e)[:50]}")
    
    print(f"\n{'='*60}")
    print("?? SUMMARY:")
    print(f"{'='*60}")
    if successful_endpoints:
        print("? Successful endpoints found:")
        for endpoint in successful_endpoints:
            print(f"   - {endpoint}")
    else:
        print("? No successful endpoints found")
        print("\n?? Suggestions:")
        print("1. Check if Xandeum has public RPC endpoints")
        print("2. Check Discord for correct endpoints")
        print("3. Might need authentication/API key")
        print("4. Could be WebSocket-only API")

asyncio.run(test_all_possible_endpoints())
