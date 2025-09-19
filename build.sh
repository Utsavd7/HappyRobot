#!/bin/bash
# build.sh

echo "Starting build process..."

# Upgrade pip first
pip install --upgrade pip

# Install packages one by one to identify any issues
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install httpx==0.25.1
pip install pydantic==2.4.2
pip install pydantic-settings==2.0.3
pip install motor==3.3.2
pip install pymongo==4.6.0
pip install redis==5.0.1
pip install python-multipart==0.0.6
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install python-dotenv==1.0.0
pip install aiofiles==23.2.1

echo "Build complete!"