#!/bin/bash

# Gemini Voice Agent - Quick Start Script

echo "🚀 Gemini Voice Agent Setup"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=AIza" .env; then
    echo "⚠️  GEMINI_API_KEY not configured in .env"
    echo "Please add your Gemini API key to .env file"
    exit 1
fi

echo "✅ Environment configured"

# Build and start containers
echo "🐳 Building Docker containers..."
docker-compose down
docker-compose build --no-cache

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."
curl -s http://localhost:8000/health | jq .

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📊 Admin Dashboard: http://localhost:3000"
echo "🔌 API Endpoint: http://localhost:8000/api"
echo "📖 Documentation: ./GEMINI_UPGRADE.md"
echo ""
echo "Next steps:"
echo "1. Open admin dashboard"
echo "2. Create a tenant"
echo "3. Add knowledge entries"
echo "4. Embed widget on your website"
echo ""
