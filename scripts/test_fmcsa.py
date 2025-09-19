import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_fmcsa():
    api_key = os.getenv('FMCSA_API_KEY')
    
    # Test with a known MC number
    test_mc = "1234567"  # Example MC number
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{test_mc}",
            params={"webKey": api_key}
        )
        
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_fmcsa())