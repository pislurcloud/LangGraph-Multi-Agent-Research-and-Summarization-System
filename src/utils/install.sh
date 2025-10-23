#!/bin/bash

# ========================================
# LangGraph Multi-Agent System Installer
# ========================================

echo "🚀 LangGraph Multi-Agent System - Installation Script"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Error: Python 3.10 or higher is required${NC}"
    echo "Current version: $python_version"
    echo "Please install Python 3.10+ and try again"
    exit 1
else
    echo -e "${GREEN}✅ Python $python_version detected${NC}"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
echo ""
echo "📥 Installing dependencies..."
echo "This may take 2-5 minutes..."

pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Error installing dependencies${NC}"
    echo "Try running: pip install -r requirements.txt"
    exit 1
fi

# Check for .env file
echo ""
echo "🔑 Checking for API keys..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your API keys:${NC}"
    echo "   - GROQ_API_KEY (get from https://console.groq.com/)"
    echo "   - TAVILY_API_KEY (get from https://tavily.com/)"
    echo ""
    echo "After adding keys, run this script again."
    exit 1
else
    # Check if API keys are set
    if grep -q "your_groq_api_key_here" .env; then
        echo -e "${YELLOW}⚠️  Please add your GROQ_API_KEY to .env${NC}"
        echo "Get it from: https://console.groq.com/"
        exit 1
    fi
    
    if grep -q "your_tavily_api_key_here" .env; then
        echo -e "${YELLOW}⚠️  Please add your TAVILY_API_KEY to .env${NC}"
        echo "Get it from: https://tavily.com/"
        exit 1
    fi
    
    echo -e "${GREEN}✅ API keys configured${NC}"
fi

# Generate dataset
echo ""
echo "📄 Generating financial dataset..."
python src/data/generate_dataset.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dataset generated${NC}"
else
    echo -e "${RED}❌ Error generating dataset${NC}"
    exit 1
fi

# Initialize vector store
echo ""
echo "🗄️  Initializing vector store..."
python src/utils/vector_store.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Vector store initialized${NC}"
else
    echo -e "${RED}❌ Error initializing vector store${NC}"
    exit 1
fi

# Run tests
echo ""
echo "🧪 Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Installation complete! All tests passed!${NC}"
    echo ""
    echo "======================================================"
    echo "Next steps:"
    echo "======================================================"
    echo ""
    echo "1. Activate the virtual environment (if not already):"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Launch the Streamlit UI:"
    echo "   streamlit run app.py"
    echo ""
    echo "3. Open your browser to:"
    echo "   http://localhost:8501"
    echo ""
    echo "4. Click '🚀 Initialize System' in the sidebar"
    echo ""
    echo "5. Start asking questions!"
    echo ""
    echo "======================================================"
    echo "Example queries:"
    echo "  - What is artificial intelligence?"
    echo "  - What's the latest AI news?"
    echo "  - What was TechNova's Q1 2024 revenue?"
    echo "======================================================"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    echo "Please check the error messages above"
    echo "See TROUBLESHOOTING.md for common solutions"
fi