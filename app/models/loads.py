# app/models/loads.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

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
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, Any], handler) -> dict[str, Any]:
        field_schema.update(type="string")
        return field_schema

class Load(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = ""
    weight: float
    commodity_type: str
    num_of_pieces: int
    miles: float
    dimensions: str
    status: str = "available"

class CallLog(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    call_id: str
    mc_number: Optional[str] = None
    load_id: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    final_rate: Optional[float] = None
    negotiation_rounds: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)