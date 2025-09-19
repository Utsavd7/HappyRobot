# app/api/endpoints/loads.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.db.sessions import get_database
from app.models.loads import Load, CallLog
from app.core.security import verify_api_key
from app.services.negotiation import negotiation_service
import logging
from bson import ObjectId

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/search")
async def search_loads(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
    min_rate: Optional[float] = None,
    max_rate: Optional[float] = None,
    api_key: str = Depends(verify_api_key)
):
    """Search for available loads based on criteria"""
    db = get_database()
    
    # Build query
    query = {"status": "available"}
    
    if origin:
        query["origin"] = {"$regex": origin, "$options": "i"}
    if destination:
        query["destination"] = {"$regex": destination, "$options": "i"}
    if equipment_type:
        query["equipment_type"] = {"$regex": equipment_type, "$options": "i"}
    if min_rate:
        query["loadboard_rate"] = {"$gte": min_rate}
    if max_rate:
        if "loadboard_rate" in query:
            query["loadboard_rate"]["$lte"] = max_rate
        else:
            query["loadboard_rate"] = {"$lte": max_rate}
    
    # Execute query
    loads_cursor = db.loads.find(query).limit(10)
    loads = []
    
    async for load in loads_cursor:
        load["_id"] = str(load["_id"])
        loads.append(load)
    
    return loads

@router.get("/{load_id}")
async def get_load(
    load_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get specific load details"""
    db = get_database()
    
    # Try to find by load_id field first
    load = await db.loads.find_one({"load_id": load_id})
    
    # If not found, try by MongoDB _id
    if not load:
        try:
            load = await db.loads.find_one({"_id": ObjectId(load_id)})
        except:
            raise HTTPException(status_code=404, detail="Load not found")
    
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    load["_id"] = str(load["_id"])
    return load

@router.post("/{load_id}/book")
async def book_load(
    load_id: str,
    mc_number: str,
    agreed_rate: float,
    api_key: str = Depends(verify_api_key)
):
    """Book a load for a carrier"""
    db = get_database()
    
    # Find the load
    load = await db.loads.find_one({"load_id": load_id})
    if not load:
        try:
            load = await db.loads.find_one({"_id": ObjectId(load_id)})
        except:
            raise HTTPException(status_code=404, detail="Load not found")
    
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    if load.get("status") != "available":
        raise HTTPException(status_code=400, detail="Load not available")
    
    # Update load status
    await db.loads.update_one(
        {"_id": load["_id"]},
        {
            "$set": {
                "status": "booked",
                "booked_by": mc_number,
                "agreed_rate": agreed_rate,
                "booked_at": datetime.utcnow()
            }
        }
    )
    
    # Log the booking
    await db.bookings.insert_one({
        "load_id": load_id,
        "mc_number": mc_number,
        "agreed_rate": agreed_rate,
        "original_rate": load.get("loadboard_rate"),
        "booked_at": datetime.utcnow()
    })
    
    return {
        "success": True,
        "load_id": load_id,
        "mc_number": mc_number,
        "agreed_rate": agreed_rate,
        "message": "Load booked successfully"
    }

@router.post("/{load_id}/negotiate")
async def negotiate_rate(
    load_id: str,
    offered_rate: float,
    negotiation_round: int = 1,
    mc_number: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Handle price negotiation for a load"""
    db = get_database()
    
    # Find the load
    load = await db.loads.find_one({"load_id": load_id})
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    # Convert to Load model for negotiation service
    load_model = Load(**load)
    
    # Evaluate the offer
    result = negotiation_service.evaluate_offer(
        load_model, 
        offered_rate, 
        negotiation_round
    )
    
    # Log negotiation attempt
    await db.negotiations.insert_one({
        "load_id": load_id,
        "mc_number": mc_number,
        "offered_rate": offered_rate,
        "negotiation_round": negotiation_round,
        "result": result,
        "timestamp": datetime.utcnow()
    })
    
    return result

@router.get("/stats/summary")
async def get_load_stats(
    api_key: str = Depends(verify_api_key)
):
    """Get summary statistics for loads"""
    db = get_database()
    
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_rate": {"$avg": "$loadboard_rate"}
            }
        }
    ]
    
    stats = []
    async for stat in db.loads.aggregate(pipeline):
        stats.append(stat)
    
    total_loads = await db.loads.count_documents({})
    booked_today = await db.loads.count_documents({
        "status": "booked",
        "booked_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
    })
    
    return {
        "total_loads": total_loads,
        "booked_today": booked_today,
        "status_breakdown": stats
    }