# scripts/seed_data.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Sample data for seeding
CITIES = [
    "Chicago, IL", "Los Angeles, CA", "Houston, TX", "Phoenix, AZ",
    "Philadelphia, PA", "San Antonio, TX", "Dallas, TX", "Austin, TX",
    "Jacksonville, FL", "Columbus, OH", "Charlotte, NC", "Indianapolis, IN",
    "Seattle, WA", "Denver, CO", "Boston, MA", "Nashville, TN",
    "Memphis, TN", "Portland, OR", "Las Vegas, NV", "Louisville, KY",
    "Milwaukee, WI", "Albuquerque, NM", "Tucson, AZ", "Fresno, CA",
    "Sacramento, CA", "Kansas City, MO", "Mesa, AZ", "Atlanta, GA",
    "Omaha, NE", "Miami, FL", "Cleveland, OH", "Oakland, CA"
]

EQUIPMENT_TYPES = ["Dry Van", "Flatbed", "Reefer", "Step Deck", "Box Truck", "Tanker"]

COMMODITIES = [
    "General Freight", "Building Materials", "Machinery", "Produce",
    "Electronics", "Paper Products", "Food Products", "Chemicals",
    "Auto Parts", "Furniture", "Steel Coils", "Lumber",
    "Consumer Goods", "Textiles", "Plastics", "Medical Supplies"
]

async def create_sample_loads(db, num_loads=50):
    """Create sample loads in the database"""
    loads = []
    
    for i in range(num_loads):
        # Generate random pickup and delivery times
        pickup_date = datetime.utcnow() + timedelta(days=random.randint(1, 14))
        delivery_date = pickup_date + timedelta(days=random.randint(1, 5))
        
        # Random cities for origin and destination
        origin = random.choice(CITIES)
        destination = random.choice([c for c in CITIES if c != origin])
        
        # Calculate approximate miles (simplified)
        miles = random.randint(100, 2500)
        
        # Calculate rate based on miles
        rate_per_mile = random.uniform(2.0, 4.5)
        loadboard_rate = round(miles * rate_per_mile, 2)
        
        load = {
            "load_id": f"LD{100000 + i}",
            "origin": origin,
            "destination": destination,
            "pickup_datetime": pickup_date.isoformat(),
            "delivery_datetime": delivery_date.isoformat(),
            "equipment_type": random.choice(EQUIPMENT_TYPES),
            "loadboard_rate": loadboard_rate,
            "notes": f"Load from {origin} to {destination}",
            "weight": random.randint(10000, 45000),
            "commodity_type": random.choice(COMMODITIES),
            "num_of_pieces": random.randint(1, 30),
            "miles": miles,
            "dimensions": f"{random.randint(20, 48)}' x {random.randint(6, 8)}' x {random.randint(6, 9)}'",
            "status": "available",
            "created_at": datetime.utcnow()
        }
        
        loads.append(load)
    
    # Insert all loads
    result = await db.loads.insert_many(loads)
    print(f"Created {len(result.inserted_ids)} sample loads")
    
    return result.inserted_ids

async def create_sample_carriers(db, num_carriers=20):
    """Create sample carrier records"""
    carriers = []
    
    for i in range(num_carriers):
        carrier = {
            "mc_number": f"MC{100000 + i}",
            "carrier_name": f"Sample Carrier {i+1}",
            "dot_number": f"DOT{200000 + i}",
            "safety_rating": random.choice(["Satisfactory", "Conditional", "None"]),
            "entity_type": "CARRIER",
            "status_code": "ACTIVE",
            "created_at": datetime.utcnow()
        }
        carriers.append(carrier)
    
    result = await db.carriers.insert_many(carriers)
    print(f"Created {len(result.inserted_ids)} sample carriers")
    
    return result.inserted_ids

async def create_indexes(db):
    """Create database indexes for better performance"""
    # Loads indexes
    await db.loads.create_index("load_id", unique=True)
    await db.loads.create_index("status")
    await db.loads.create_index("origin")
    await db.loads.create_index("destination")
    await db.loads.create_index("equipment_type")
    await db.loads.create_index("loadboard_rate")
    
    # Carriers indexes
    await db.carriers.create_index("mc_number", unique=True)
    await db.carriers.create_index("dot_number")
    
    # Call logs indexes
    await db.call_logs.create_index("call_id")
    await db.call_logs.create_index("mc_number")
    await db.call_logs.create_index("created_at")
    
    print("Created database indexes")

async def main():
    """Main function to seed the database"""
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.carrier_loads
    
    try:
        print("Starting database seeding...")
        
        # Clear existing data (optional - comment out in production)
        await db.loads.delete_many({})
        await db.carriers.delete_many({})
        await db.call_logs.delete_many({})
        print("Cleared existing data")
        
        # Create indexes
        await create_indexes(db)
        
        # Create sample data
        await create_sample_loads(db, num_loads=50)
        await create_sample_carriers(db, num_carriers=20)
        
        # Verify data
        load_count = await db.loads.count_documents({})
        carrier_count = await db.carriers.count_documents({})
        
        print(f"\nDatabase seeding complete!")
        print(f"Total loads: {load_count}")
        print(f"Total carriers: {carrier_count}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())