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

@router.post("/search", response_model=List[LoadResponse])
async def search_loads(
    search: LoadSearch,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Search for available loads based on criteria"""
    query = db.query(Load).filter(Load.status == "available")
    
    if search.origin:
        query = query.filter(Load.origin.ilike(f"%{search.origin}%"))
    if search.destination:
        query = query.filter(Load.destination.ilike(f"%{search.destination}%"))
    if search.equipment_type:
        query = query.filter(Load.equipment_type.ilike(f"%{search.equipment_type}%"))
    if search.min_rate:
        query = query.filter(Load.loadboard_rate >= search.min_rate)
    if search.max_rate:
        query = query.filter(Load.loadboard_rate <= search.max_rate)
    
    loads = query.limit(10).all()
    return loads

@router.get("/{load_id}", response_model=LoadResponse)
async def get_load(
    load_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific load details"""
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load

@router.post("/{load_id}/book")
async def book_load(
    load_id: str,
    mc_number: str,
    agreed_rate: float,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Book a load for a carrier"""
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    if load.status != "available":
        raise HTTPException(status_code=400, detail="Load not available")
    
    # Update load status
    load.status = "booked"
    db.commit()
    
    return {
        "success": True,
        "load_id": load_id,
        "mc_number": mc_number,
        "agreed_rate": agreed_rate,
        "message": "Load booked successfully"
    }