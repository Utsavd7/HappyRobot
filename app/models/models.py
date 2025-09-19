from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class LoadStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class CallOutcome(str, Enum):
    BOOKED = "booked"
    NEGOTIATION_FAILED = "negotiation_failed"
    NOT_INTERESTED = "not_interested"
    TRANSFERRED = "transferred"
    DROPPED = "dropped"
    VERIFICATION_FAILED = "verification_failed"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Load(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    load_id: str = Field(..., description="Unique identifier for the load")
    origin: str = Field(..., description="Starting location")
    destination: str = Field(..., description="Delivery location")
    pickup_datetime: datetime = Field(..., description="Date and time for pickup")
    delivery_datetime: datetime = Field(..., description="Date and time for delivery")
    equipment_type: str = Field(..., description="Type of equipment needed")
    loadboard_rate: float = Field(..., description="Listed rate for the load")
    notes: Optional[str] = Field(default="", description="Additional information")
    weight: float = Field(..., description="Load weight in pounds")
    commodity_type: str = Field(..., description="Type of goods")
    num_of_pieces: int = Field(..., description="Number of items")
    miles: float = Field(..., description="Distance to travel")
    dimensions: str = Field(..., description="Size measurements")
    status: LoadStatus = Field(default=LoadStatus.AVAILABLE)
    booked_mc_number: Optional[str] = None
    booked_rate: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "load_id": "LD-2024-001",
                "origin": "Chicago, IL",
                "destination": "Atlanta, GA",
                "pickup_datetime": "2024-01-15T08:00:00Z",
                "delivery_datetime": "2024-01-16T18:00:00Z",
                "equipment_type": "Dry Van",
                "loadboard_rate": 2500.00,
                "weight": 35000,
                "commodity_type": "General Freight",
                "num_of_pieces": 24,
                "miles": 716,
                "dimensions": "48x40x48"
            }
        }

class CallLog(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    call_id: str = Field(..., description="Unique call identifier")
    mc_number: Optional[str] = Field(None, description="Carrier MC number")
    carrier_name: Optional[str] = None
    load_id: Optional[str] = Field(None, description="Associated load ID")
    outcome: Optional[CallOutcome] = None
    sentiment: Optional[Sentiment] = None
    initial_offer: Optional[float] = None
    final_rate: Optional[float] = None
    negotiation_rounds: int = Field(default=0)
    negotiation_history: List[dict] = Field(default_factory=list)
    call_duration: Optional[int] = Field(None, description="Duration in seconds")
    verification_status: Optional[str] = None
    transfer_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Carrier(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mc_number: str = Field(..., unique=True)
    legal_name: str
    entity_type: str
    status_code: str
    safety_rating: Optional[str] = None
    is_eligible: bool
    last_verified: datetime = Field(default_factory=datetime.utcnow)
    total_calls: int = Field(default=0)
    successful_bookings: int = Field(default=0)
    average_rate: Optional[float] = None
    preferred_equipment: List[str] = Field(default_factory=list)
    preferred_lanes: List[dict] = Field(default_factory=list)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}