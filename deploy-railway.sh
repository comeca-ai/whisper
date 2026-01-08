# =============================================================================
# RAILWAY DEPLOYMENT SCRIPT - WHISPER ENHANCED
# =============================================================================

#!/bin/bash

set -e  # Exit on any error

echo "🚂 Railway Deploy - Whisper Enhanced"
echo "====================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found. Installing...${NC}"
    curl -fsSL https://railway.app/install.sh | sh
    export PATH=$PATH:~/.railway/bin
fi

# Login check
echo -e "${YELLOW}🔐 Checking Railway authentication...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️ Not logged in to Railway. Please login:${NC}"
    railway login
fi

# Project selection/creation
echo -e "${YELLOW}📁 Setting up Railway project...${NC}"
if [ ! -f "railway.toml" ]; then
    echo -e "${RED}❌ railway.toml not found in current directory${NC}"
    exit 1
fi

# Initialize project if needed
if ! railway status &> /dev/null; then
    echo -e "${YELLOW}🆕 Creating new Railway project...${NC}"
    railway project create whisper-enhanced
fi

# Set environment variables
echo -e "${YELLOW}⚙️ Setting production environment variables...${NC}"
railway variables set PORT=8000
railway variables set PYTHONUNBUFFERED=1
railway variables set WHISPER_MODEL=base
railway variables set COMPRESSION_RATIO_THRESHOLD=1.8
railway variables set CONDITION_ON_PREVIOUS_TEXT=false
railway variables set CLEAN_REPETITIONS=true
railway variables set APPLY_CORRECTIONS=true
railway variables set MAX_FILE_SIZE=26214400

# Build and deploy
echo -e "${YELLOW}🚀 Building and deploying to Railway...${NC}"
railway deploy --dockerfile Dockerfile.railway

echo ""
echo -e "${GREEN}✅ Deploy completed!${NC}"
echo ""
echo "📊 Check your deployment status:"
echo "  railway status"
echo ""
echo "📱 View your app:"
echo "  railway open"
echo ""
echo "📋 View logs:"
echo "  railway logs"
echo ""
echo "🔧 Environment variables:"
echo "  railway variables"
echo ""
echo -e "${GREEN}🎯 Your Whisper API is now live!${NC}"
echo ""
echo "API Endpoints:"
echo "  POST /transcribe - Main transcription endpoint"
echo "  GET /health - Health check"
echo "  GET /models - Available models"
echo ""
echo "Example usage:"
echo '  curl -X POST "https://your-app.railway.app/transcribe" \'
echo '    -F "file=@audio.mp3" \'
echo '    -F "model=base" \'
echo '    -F "clean_repetitions=true"'
echo ""
echo -e "${YELLOW}📚 Documentation: docs/README_API.md${NC}"