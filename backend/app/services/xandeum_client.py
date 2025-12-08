import aiohttp
import asyncio
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import random
import string

logger = logging.getLogger(__name__)

class XandeumPRPCClient:
    """Xandeum pRPC Client - Demo Mode
    Note: Public Xandeum RPC endpoints are not available.
    This simulates what the dashboard would look like with real data.
    """
    
    def __init__(self, network: str = "testnet"):
        self.network = network
        self.is_real_data = False  # Important flag
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
            
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_pnodes(self) -> List[Dict]:
        """Get realistic mock pNode data for demo"""
        logger.info(f"Generating realistic demo data for {self.network}")
        
        pnodes = []
        base_time = datetime.utcnow()
        
        # Generate different node types
        node_types = [
            {"performance": 0.95, "uptime": 99.9, "stake": 5000000, "commission": 1.5, "count": 5},
            {"performance": 0.85, "uptime": 98.5, "stake": 2000000, "commission": 3.0, "count": 10},
            {"performance": 0.75, "uptime": 95.0, "stake": 1000000, "commission": 5.0, "count": 10},
            {"performance": 0.60, "uptime": 88.0, "stake": 500000, "commission": 8.0, "count": 5},
        ]
        
        node_counter = 0
        for node_type in node_types:
            for i in range(node_type["count"]):
                node_counter += 1
                is_active = random.random() > 0.1  # 90% active
                last_seen_offset = random.randint(0, 300)  # 0-5 minutes ago
                
                pnode = {
                    "pubkey": f"xnd_{self.network[:3]}_{''.join(random.choices(string.hexdigits.lower(), k=44))}",
                    "ip": f"{random.randint(10, 200)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                    "version": self._generate_version(),
                    "is_active": is_active,
                    "last_seen": (base_time - timedelta(seconds=last_seen_offset)).isoformat(),
                    "stake": node_type["stake"] + random.randint(-100000, 100000),
                    "commission": node_type["commission"] + random.uniform(-0.5, 0.5),
                    "data_center": self._generate_data_center(),
                    "performance_score": node_type["performance"] + random.uniform(-0.05, 0.05),
                    "uptime_24h": node_type["uptime"] + random.uniform(-1, 1),
                    "vote_success_rate": 98.5 + random.uniform(-2, 1),
                    "response_time_ms": random.randint(80, 250),
                    "peer_count": random.randint(30, 120),
                    "network": self.network,
                    "is_real_data": False,
                    "status": "active" if is_active else "inactive",
                    "location": self._generate_location(),
                    "last_vote": random.randint(1000000, 2000000) if is_active else 0,
                    "epoch_credits": random.randint(1000, 10000) if is_active else 0,
                }
                pnodes.append(pnode)
        
        # Sort by stake (highest first)
        pnodes.sort(key=lambda x: x["stake"], reverse=True)
        
        logger.info(f"Generated {len(pnodes)} realistic pNodes for {self.network} demo")
        return pnodes
    
    def _generate_version(self) -> str:
        versions = ["1.2.0", "1.1.5", "1.1.4", "1.1.3", "1.1.2"]
        weights = [0.6, 0.2, 0.1, 0.05, 0.05]
        return random.choices(versions, weights=weights)[0]
    
    def _generate_data_center(self) -> str:
        providers = ["AWS", "Google Cloud", "Microsoft Azure", "DigitalOcean", "Hetzner", "OVH"]
        regions = ["us-east-1", "us-west-2", "eu-west-1", "asia-southeast-1", "eu-central-1"]
        return f"{random.choice(providers)} {random.choice(regions)}"
    
    def _generate_location(self) -> str:
        # Using ASCII-only locations to avoid encoding issues
        locations = [
            "New York, USA", "London, UK", "Singapore", "Tokyo, Japan",
            "Frankfurt, Germany", "Sydney, Australia", "Sao Paulo, Brazil",
            "Mumbai, India", "Paris, France", "Toronto, Canada"
        ]
        return random.choice(locations)
    
    async def get_network_info(self) -> Dict:
        """Generate realistic network information"""
        # Simulate network progression
        base_epoch = 250
        base_slot = 1520000
        
        # Add some randomness and progression
        time_factor = int(datetime.utcnow().timestamp() / 1000)
        current_slot = base_slot + (time_factor % 10000)
        current_epoch = base_epoch + (current_slot // 432000)  # ~432000 slots per epoch
        
        return {
            "epoch": current_epoch,
            "slot": current_slot,
            "absolute_slot": current_slot,
            "block_height": current_slot - 1000,
            "transaction_count": random.randint(5000000, 10000000),
            "current_validators": random.randint(20, 40),
            "total_active_stake": random.randint(500000000, 1000000000),
            "average_commission": round(random.uniform(3.0, 6.0), 2),
            "network_version": "1.2.0",
            "is_real_data": False,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Demo mode - Xandeum public RPC endpoints not available"
        }
    
    async def get_pnode_details(self, pubkey: str) -> Optional[Dict]:
        """Get detailed information about a specific pNode"""
        # Generate consistent details based on pubkey
        random.seed(pubkey)  # Seed for consistency
        
        is_active = "inactive" not in pubkey
        stake = random.randint(100000, 10000000)
        
        return {
            "pubkey": pubkey,
            "status": "active" if is_active else "inactive",
            "uptime_24h": round(random.uniform(85.0, 99.9), 1),
            "uptime_7d": round(random.uniform(88.0, 99.5), 1),
            "uptime_30d": round(random.uniform(90.0, 99.0), 1),
            "vote_success_rate": round(random.uniform(95.0, 99.9), 1),
            "response_time_ms": random.randint(50, 300),
            "peer_count": random.randint(20, 150),
            "total_stake": stake,
            "commission": round(random.uniform(0.5, 10.0), 2),
            "last_updated": datetime.utcnow().isoformat(),
            "version": self._generate_version(),
            "data_center": self._generate_data_center(),
            "location": self._generate_location(),
            "latency_ms": random.randint(20, 200),
            "reliability_score": round(random.uniform(0.7, 1.0), 3),
            "epoch_credits": random.randint(1000, 10000) if is_active else 0,
            "last_vote": random.randint(1000000, 2000000) if is_active else 0,
            "root_slot": random.randint(1000000, 2000000) if is_active else 0,
            "is_real_data": False,
            "notes": "Demo data - Real Xandeum API endpoints not publicly available"
        }
