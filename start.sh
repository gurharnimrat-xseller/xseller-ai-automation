#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Xseller.ai Full-Stack Application${NC}"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}Port $1 is already in use!${NC}"
        exit 1
    fi
}

# Check if ports are available
echo -e "${YELLOW}Checking ports...${NC}"
check_port 8000
check_port 3000

# Create virtual environment if it doesn't exist
echo -e "${YELLOW}Setting up backend...${NC}"
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
fi

# Start backend server in background
echo -e "${GREEN}Starting backend server on port 8000...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}Backend failed to start!${NC}"
    cat ../backend.log
    exit 1
fi

echo -e "${GREEN}Backend started successfully (PID: $BACKEND_PID)${NC}"

# Move to frontend directory
cd ../frontend || exit 1

# Install Node dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
fi

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
npm run build

# Start frontend server
echo -e "${GREEN}Starting frontend server on port 3000...${NC}"
exec npm run start

