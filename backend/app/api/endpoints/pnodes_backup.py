from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from app.services.xandeum_client import XandeumPRPCClient

router = APIRouter(prefix="/pnodes", tags=["pNodes"])

# Initialize client (will be created per request to handle network switching)
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
    
    - **network**: "testnet" or "mainnet" or "demo"
    - **skip**: Number of pNodes to skip
    - **limit**: Maximum number to return
    - **active_only**: Only return active pNodes
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
            "pnodes": paginated_pnodes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pNodes: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Error fetching pNode details: {str(e)}")

@router.get("/stats/summary")
async def get_pnode_summary(network: Optional[str] = "testnet"):
    """Get summary statistics about all pNodes"""
    try:
        client = get_client(network)
        pnodes = await client.get_pnodes()
        
        if not pnodes:
            return {
                "network": network,
                "total_pnodes": 0,
                "active_pnodes": 0,
                "inactive_pnodes": 0,
                "total_stake": 0,
                "avg_commission": 0,
                "avg_performance": 0
            }
        
        active_pnodes = [p for p in pnodes if p.get("is_active", False)]
        total_stake = sum(p.get("stake", 0) for p in active_pnodes)
        
        commissions = [p.get("commission", 0) for p in active_pnodes if p.get("stake", 0) > 0]
        avg_commission = sum(commissions) / len(commissions) if commissions else 0
        
        performances = [p.get("performance_score", 0) for p in active_pnodes]
        avg_performance = sum(performances) / len(performances) if performances else 0
        
        return {
            "network": network,
            "total_pnodes": len(pnodes),
            "active_pnodes": len(active_pnodes),
            "inactive_pnodes": len(pnodes) - len(active_pnodes),
            "total_stake": total_stake,
            "avg_commission": round(avg_commission, 2),
            "avg_performance": round(avg_performance, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating summary: {str(e)}")

@router.get("/network/info")
async def get_network_information(network: Optional[str] = "testnet"):
    """Get network information"""
    try:
        client = get_client(network)
        info = await client.get_network_info()
        return {
            "network": network,
            **info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting network info: {str(e)}")
