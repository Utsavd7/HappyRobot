# app/api/endpoints/webhooks.py
from fastapi import APIRouter, HTTPException, Request, Response
from typing import Dict, Any, Optional
from datetime import datetime
from app.db.sessions import get_database
from app.api.endpoints.carriers import verify_carrier
from app.api.endpoints.loads import search_loads, negotiate_rate, book_load
from app.models.loads import CallLog
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/happyrobot/voice")
async def handle_voice_webhook(request: Request):
    """
    Handle incoming webhook from HappyRobot voice agent
    This will be called during the conversation to perform actions
    """
    try:
        payload = await request.json()
        logger.info(f"Received webhook: {json.dumps(payload, indent=2)}")
        
        # Extract key information from the webhook
        session_id = payload.get("session_id")
        action = payload.get("action")
        parameters = payload.get("parameters", {})
        
        # Route based on action
        if action == "verify_carrier":
            return await handle_carrier_verification(parameters)
        
        elif action == "search_loads":
            return await handle_load_search(parameters)
        
        elif action == "negotiate_rate":
            return await handle_negotiation(parameters)
        
        elif action == "book_load":
            return await handle_booking(parameters)
        
        elif action == "log_call":
            return await log_call_data(session_id, parameters)
        
        else:
            return {"error": f"Unknown action: {action}"}
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_carrier_verification(params: Dict[str, Any]):
    """Verify carrier using MC number"""
    mc_number = params.get("mc_number")
    if not mc_number:
        return {
            "success": False,
            "message": "MC number is required for verification"
        }
    
    try:
        # Call the verification endpoint
        result = await verify_carrier(mc_number, api_key="internal")
        
        return {
            "success": True,
            "is_eligible": result["is_eligible"],
            "carrier_name": result.get("carrier_name", "Unknown"),
            "safety_rating": result.get("safety_rating", "Not Rated"),
            "message": f"Carrier {result['carrier_name']} verified successfully" if result["is_eligible"] 
                      else "Carrier is not eligible to book loads"
        }
    except Exception as e:
        logger.error(f"Carrier verification failed: {str(e)}")
        return {
            "success": False,
            "message": "Unable to verify carrier at this time"
        }

async def handle_load_search(params: Dict[str, Any]):
    """Search for loads based on carrier criteria"""
    try:
        # Extract search parameters
        origin = params.get("origin")
        destination = params.get("destination")
        equipment_type = params.get("equipment_type")
        
        # Search for loads
        loads = await search_loads(
            origin=origin,
            destination=destination,
            equipment_type=equipment_type,
            api_key="internal"
        )
        
        if not loads:
            return {
                "success": True,
                "loads": [],
                "message": "No loads currently available matching your criteria"
            }
        
        # Format loads for voice response
        formatted_loads = []
        for load in loads[:3]:  # Limit to top 3 for voice
            formatted_loads.append({
                "load_id": load["load_id"],
                "origin": load["origin"],
                "destination": load["destination"],
                "rate": load["loadboard_rate"],
                "pickup": load["pickup_datetime"],
                "delivery": load["delivery_datetime"],
                "miles": load.get("miles", 0),
                "weight": load.get("weight", 0),
                "commodity": load.get("commodity_type", "General freight")
            })
        
        return {
            "success": True,
            "loads": formatted_loads,
            "message": f"Found {len(formatted_loads)} loads matching your criteria"
        }
        
    except Exception as e:
        logger.error(f"Load search failed: {str(e)}")
        return {
            "success": False,
            "message": "Unable to search loads at this time"
        }

async def handle_negotiation(params: Dict[str, Any]):
    """Handle rate negotiation"""
    try:
        load_id = params.get("load_id")
        offered_rate = params.get("offered_rate")
        negotiation_round = params.get("negotiation_round", 1)
        mc_number = params.get("mc_number")
        
        # Call negotiation service
        result = await negotiate_rate(
            load_id=load_id,
            offered_rate=offered_rate,
            negotiation_round=negotiation_round,
            mc_number=mc_number,
            api_key="internal"
        )
        
        return {
            "success": True,
            "action": result["action"],
            "message": result["message"],
            "counter_rate": result.get("counter_rate"),
            "accepted": result.get("accepted", False)
        }
        
    except Exception as e:
        logger.error(f"Negotiation failed: {str(e)}")
        return {
            "success": False,
            "message": "Unable to process negotiation"
        }

async def handle_booking(params: Dict[str, Any]):
    """Book a load for a carrier"""
    try:
        load_id = params.get("load_id")
        mc_number = params.get("mc_number")
        agreed_rate = params.get("agreed_rate")
        
        # Book the load
        result = await book_load(
            load_id=load_id,
            mc_number=mc_number,
            agreed_rate=agreed_rate,
            api_key="internal"
        )
        
        return {
            "success": True,
            "message": result["message"],
            "booking_details": {
                "load_id": load_id,
                "mc_number": mc_number,
                "agreed_rate": agreed_rate
            }
        }
        
    except Exception as e:
        logger.error(f"Booking failed: {str(e)}")
        return {
            "success": False,
            "message": "Unable to book load at this time"
        }

async def log_call_data(session_id: str, params: Dict[str, Any]):
    """Log call data for reporting"""
    try:
        db = get_database()
        
        call_log = {
            "call_id": session_id,
            "mc_number": params.get("mc_number"),
            "load_id": params.get("load_id"),
            "outcome": params.get("outcome"),
            "sentiment": params.get("sentiment"),
            "final_rate": params.get("final_rate"),
            "negotiation_rounds": params.get("negotiation_rounds", 0),
            "duration": params.get("duration"),
            "transcript": params.get("transcript", []),
            "created_at": datetime.utcnow()
        }
        
        await db.call_logs.insert_one(call_log)
        
        return {
            "success": True,
            "message": "Call data logged successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to log call data: {str(e)}")
        return {
            "success": False,
            "message": "Failed to log call data"
        }

@router.post("/happyrobot/status")
async def handle_status_webhook(request: Request):
    """Handle call status updates from HappyRobot"""
    payload = await request.json()
    logger.info(f"Call status update: {json.dumps(payload, indent=2)}")
    
    # You can log call completion, transfers, errors, etc.
    db = get_database()
    
    await db.call_events.insert_one({
        "timestamp": datetime.utcnow(),
        "event_type": "status_update",
        "payload": payload
    })
    
    return {"received": True}