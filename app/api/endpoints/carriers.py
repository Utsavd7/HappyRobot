from fastapi import APIRouter, HTTPException, Depends
import httpx
from app.core.config import settings
from app.core.security import verify_api_key
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/verify")
async def verify_carrier(mc_number: str, api_key: str = Depends(verify_api_key)):
    """Verify carrier using FMCSA API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{mc_number}",
                params={"webKey": settings.fmcsa_api_key}
            )
            
        if response.status_code == 200:
            data = response.json()
            carrier = data.get("content", {}).get("carrier", {})
            
            return {
                "mc_number": mc_number,
                "is_eligible": (
                    carrier.get("entityType") == "CARRIER" and
                    carrier.get("statusCode") == "ACTIVE"
                ),
                "carrier_name": carrier.get("legalName", "Unknown"),
                "safety_rating": carrier.get("safetyRating", "Not Rated")
            }
        else:
            return {"mc_number": mc_number, "is_eligible": False, "error": "Not found"}
            
    except Exception as e:
        logger.error(f"FMCSA verification failed: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")