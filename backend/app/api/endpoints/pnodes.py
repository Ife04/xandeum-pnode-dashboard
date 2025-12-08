from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime
import random
from app.services.xandeum_client import XandeumPRPCClient

router = APIRouter(prefix="/pnodes", tags=["pNodes"])

def get_client(network: str = "testnet"):
    return XandeumPRPCClient(network=network)

@router.get("/")
async def get_all_pnodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = False,
    network: Optional[str] = "testnet"
):
    """
    Get all pNodes with pagination.
    
    Note: Returns realistic demo data since Xandeum public RPC endpoints are not available.
    """
    try:
        client = get_client(network)
        pnodes = await client.get_pnodes()
        
        if active_only:
            pnodes = [p for p in pnodes if p.get("is_active", False)]
        
        total = len(pnodes)
        paginated_pnodes = pnodes[skip:skip + limit]
        
        return {
            "network": network,
            "total": total,
            "skip": skip,
            "limit": limit,
            "active_only": active_only,
            "is_real_data": False,
            "note": "Demo data - Ready for real Xandeum API integration",
            "pnodes": paginated_pnodes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/{pubkey}")
async def get_pnode_by_pubkey(pubkey: str, network: Optional[str] = "testnet"):
    """Get detailed information about a specific pNode"""
    try:
        client = get_client(network)
        details = await client.get_pnode_details(pubkey)
        if not details:
            raise HTTPException(status_code=404, detail=f"pNode {pubkey} not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/stats/summary")
async def get_pnode_summary(network: Optional[str] = "testnet"):
    """Get summary statistics - Demo data showing dashboard capability"""
    try:
        client = get_client(network)
        pnodes = await client.get_pnodes()
        network_info = await client.get_network_info()
        
        if not pnodes:
            return {
                "network": network,
                "total_pnodes": 0,
                "active_pnodes": 0,
                "inactive_pnodes": 0,
                "total_stake": 0,
                "avg_commission": 0,
                "avg_performance": 0,
                "is_real_data": False
            }
        
        active_pnodes = [p for p in pnodes if p.get("is_active", False)]
        total_stake = sum(p.get("stake", 0) for p in active_pnodes)
        
        commissions = [p.get("commission", 0) for p in active_pnodes if p.get("stake", 0) > 0]
        avg_commission = sum(commissions) / len(commissions) if commissions else 0
        
        performances = [p.get("performance_score", 0) for p in active_pnodes]
        avg_performance = sum(performances) / len(performances) if performances else 0
        
        # Calculate some additional stats
        high_performers = len([p for p in active_pnodes if p.get("performance_score", 0) > 0.9])
        low_commission = len([p for p in active_pnodes if p.get("commission", 0) < 3.0])
        
        return {
            "network": network,
            "total_pnodes": len(pnodes),
            "active_pnodes": len(active_pnodes),
            "inactive_pnodes": len(pnodes) - len(active_pnodes),
            "total_stake": total_stake,
            "avg_commission": round(avg_commission, 2),
            "avg_performance": round(avg_performance, 3),
            "high_performers": high_performers,
            "low_commission_nodes": low_commission,
            "current_epoch": network_info.get("epoch", 0),
            "current_slot": network_info.get("slot", 0),
            "block_height": network_info.get("block_height", 0),
            "network_version": network_info.get("network_version", "1.2.0"),
            "is_real_data": False,
            "demo_note": "Realistic simulation - Dashboard ready for Xandeum API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/network/info")
async def get_network_information(network: Optional[str] = "testnet"):
    """Get network information - Demo data"""
    try:
        client = get_client(network)
        info = await client.get_network_info()
        return {
            "network": network,
            **info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "xandeum-pnode-dashboard",
        "version": "2.0.0",
        "mode": "demo",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Dashboard operational. Ready for Xandeum API integration."
    }
