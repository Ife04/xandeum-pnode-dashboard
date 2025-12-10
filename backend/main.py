from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI(
    title="Xandeum pNode Dashboard API",
    description="Demo dashboard - Ready for Xandeum API integration",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_mock_pnodes(network="testnet", count=30):
    """Generate realistic mock pNode data"""
    import string
    from datetime import datetime, timedelta
    
    pnodes = []
    for i in range(count):
        is_active = random.random() > 0.2
        stake = random.randint(100000, 10000000)
        commission = random.uniform(0.5, 10.0)
        
        pnodes.append({
            "pubkey": f"{network[:3]}_{''.join(random.choices(string.hexdigits.lower(), k=40))}",
            "ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "version": f"1.{random.randint(0,2)}.{random.randint(0,9)}",
            "is_active": is_active,
            "last_seen": (datetime.utcnow() - timedelta(minutes=random.randint(0, 60))).isoformat(),
            "stake": stake,
            "commission": round(commission, 2),
            "data_center": random.choice(["AWS us-east-1", "Google Cloud europe-west", "Azure asia-east"]),
            "performance_score": round(random.uniform(0.7, 1.0), 3),
            "network": network
        })
    
    # Sort by stake
    pnodes.sort(key=lambda x: x["stake"], reverse=True)
    return pnodes

@app.get("/")
async def root():
    return {
        "service": "Xandeum pNode Dashboard API",
        "status": "running",
        "mode": "demo",
        "note": "Demo mode - Ready for Xandeum API integration",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "pnodes": "/pnodes",
            "pnodes_summary": "/pnodes/stats/summary"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/pnodes")
async def get_pnodes(network: str = "testnet", skip: int = 0, limit: int = 100):
    """Get pNodes with pagination"""
    pnodes = generate_mock_pnodes(network, count=50)
    total = len(pnodes)
    paginated = pnodes[skip:skip + limit]
    
    return {
        "network": network,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pnodes": paginated,
        "is_real_data": False,
        "note": "Demo data - Dashboard ready for Xandeum API"
    }

@app.get("/pnodes/stats/summary")
async def get_summary(network: str = "testnet"):
    """Get summary statistics"""
    pnodes = generate_mock_pnodes(network, count=50)
    active = [p for p in pnodes if p["is_active"]]
    
    if not active:
        return {
            "network": network,
            "total_pnodes": len(pnodes),
            "active_pnodes": 0,
            "total_stake": 0,
            "avg_commission": 0,
            "avg_performance": 0,
            "is_real_data": False
        }
    
    total_stake = sum(p["stake"] for p in active)
    avg_commission = sum(p["commission"] for p in active) / len(active)
    avg_performance = sum(p["performance_score"] for p in active) / len(active)
    
    return {
        "network": network,
        "total_pnodes": len(pnodes),
        "active_pnodes": len(active),
        "inactive_pnodes": len(pnodes) - len(active),
        "total_stake": total_stake,
        "avg_commission": round(avg_commission, 2),
        "avg_performance": round(avg_performance, 3),
        "current_epoch": random.randint(200, 300),
        "current_slot": random.randint(1500000, 1600000),
        "is_real_data": False,
        "demo_note": "Realistic simulation - Ready for Xandeum API"
    }

@app.get("/pnodes/{pubkey}")
async def get_pnode(pubkey: str, network: str = "testnet"):
    """Get pNode details"""
    return {
        "pubkey": pubkey,
        "network": network,
        "status": "active",
        "uptime_24h": round(random.uniform(95.0, 99.9), 1),
        "stake": random.randint(100000, 10000000),
        "commission": round(random.uniform(1.0, 8.0), 2),
        "performance": round(random.uniform(0.8, 1.0), 3),
        "version": "1.2.0",
        "is_real_data": False,
        "last_updated": datetime.utcnow().isoformat()
    }
