#!/bin/bash

# 🚀 Smart Travel Optimizer - Quick Setup Script
# This script helps you set up API keys and test the application

set -e

echo "🛫 Smart Travel Optimizer - API Keys Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local default="$2"
    local secret="$3"
    
    if [ "$secret" = "true" ]; then
        echo -n -e "${BLUE}$prompt${NC}"
        read -s input
        echo
    else
        echo -n -e "${BLUE}$prompt${NC}"
        if [ -n "$default" ]; then
            echo -n " (default: $default): "
        else
            echo -n ": "
        fi
        read input
    fi
    
    if [ -z "$input" ] && [ -n "$default" ]; then
        input="$default"
    fi
    
    echo "$input"
}

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Backing up to .env.backup${NC}"
    cp .env .env.backup
else
    echo -e "${GREEN}✅ Creating new .env file from template${NC}"
    cp .env.example .env
fi

echo ""
echo -e "${BLUE}📋 Let's set up your API keys step by step...${NC}"
echo ""

# 1. SMTP Configuration
echo -e "${YELLOW}1. 📧 Email Configuration (for sending results)${NC}"
echo "   You can skip this if you don't want email functionality"
echo ""

smtp_host=$(prompt_input "SMTP Host" "smtp.gmail.com")
smtp_port=$(prompt_input "SMTP Port" "587")
smtp_username=$(prompt_input "SMTP Username (your email)")
smtp_password=$(prompt_input "SMTP Password (Gmail App Password)" "" "true")
smtp_from_name=$(prompt_input "From Name" "Smart Travel Optimizer")

# 2. Amadeus Configuration
echo ""
echo -e "${YELLOW}2. 🛫 Amadeus API (Flight Data)${NC}"
echo "   Visit: https://developers.amadeus.com/"
echo "   Create account → Create App → Get API Key & Secret"
echo ""

read -p "Do you have Amadeus API credentials? (y/N): " has_amadeus
if [[ $has_amadeus =~ ^[Yy]$ ]]; then
    amadeus_key=$(prompt_input "Amadeus API Key")
    amadeus_secret=$(prompt_input "Amadeus API Secret" "" "true")
else
    echo -e "${BLUE}ℹ️  Skipping Amadeus - you can add this later${NC}"
    amadeus_key=""
    amadeus_secret=""
fi

# 3. Omio Configuration
echo ""
echo -e "${YELLOW}3. 🚂 Omio API (Train/Bus Data)${NC}"
echo "   Visit: https://www.omio.com/partners"
echo "   Apply for partnership → Get API Key"
echo ""

read -p "Do you have Omio API credentials? (y/N): " has_omio
if [[ $has_omio =~ ^[Yy]$ ]]; then
    omio_key=$(prompt_input "Omio API Key")
else
    echo -e "${BLUE}ℹ️  Skipping Omio - you can add this later${NC}"
    omio_key=""
fi

# 4. Write to .env file
echo ""
echo -e "${GREEN}💾 Writing configuration to .env file...${NC}"

cat > .env << EOF
# ============================================================================
# Smart Travel Optimizer - Environment Configuration
# Generated on $(date)
# ============================================================================

# Email (SMTP) Configuration
SMTP_HOST=$smtp_host
SMTP_PORT=$smtp_port
SMTP_USERNAME=$smtp_username
SMTP_PASSWORD=$smtp_password
SMTP_FROM_NAME=$smtp_from_name

# Travel API Providers
AMADEUS_API_KEY=$amadeus_key
AMADEUS_API_SECRET=$amadeus_secret
OMIO_API_KEY=$omio_key

# Security Settings
RATE_LIMIT_REQUESTS_PER_MINUTE=60
MAX_EMAIL_SIZE_KB=1024

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
EOF

echo -e "${GREEN}✅ Configuration saved to .env${NC}"

# 5. Test configuration
echo ""
echo -e "${YELLOW}🧪 Testing configuration...${NC}"

# Check Python environment
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}📦 Creating Python virtual environment...${NC}"
    python -m venv .venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Test import
echo -e "${BLUE}🔍 Testing application import...${NC}"
python -c "
try:
    from src.config import USE_AMADEUS, USE_OMIO
    print(f'✅ Configuration loaded successfully')
    print(f'   - Amadeus: {\"Enabled\" if USE_AMADEUS else \"Disabled\"}')
    print(f'   - Omio: {\"Enabled\" if USE_OMIO else \"Disabled\"}')
    print(f'   - Mock Provider: Always Available')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

# Test mock provider
echo -e "${BLUE}🧪 Running test query with Mock Provider...${NC}"
python -c "
try:
    from src.agents.route_agent import plan_best_routes
    results = plan_best_routes('Stuttgart', 'Vienna', '2025-10-01')
    if results:
        print(f'✅ Mock Provider test successful - Found {len(results)} routes')
        print(f'   Best option: {results[0][\"mode\"].title()} via {results[0].get(\"airline\", results[0].get(\"carrier\", \"Unknown\"))} - €{results[0][\"price_eur\"]}')
    else:
        print('⚠️  Mock Provider returned no results - check sample data')
except Exception as e:
    print(f'❌ Test failed: {e}')
"

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""
echo "1. 🧪 Test the CLI application:"
echo "   python main.py --origin \"Stuttgart\" --destination \"Vienna\" --date \"2025-10-01\""
echo ""
echo "2. 🌐 Start the web interface:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "3. 📖 Read the documentation:"
echo "   - API Keys: docs/API_KEYS_SETUP.md"
echo "   - README: README.md"
echo ""
echo "4. 🔑 To add more API keys later:"
echo "   - Edit .env file directly"
echo "   - Or run this script again"
echo ""

if [ -n "$amadeus_key" ] || [ -n "$omio_key" ]; then
    echo -e "${YELLOW}🔐 Security Reminder:${NC}"
    echo "   - Never commit your .env file to version control"
    echo "   - Keep your API keys secure and rotate them regularly"
    echo "   - Monitor your API usage to avoid unexpected charges"
    echo ""
fi

echo -e "${GREEN}Happy travels! ✈️🚂🚌${NC}"
