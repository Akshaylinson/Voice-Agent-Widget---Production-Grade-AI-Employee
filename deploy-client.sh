#!/bin/bash

# Deploy new client instance
# Usage: ./deploy-client.sh <client_id> <port>

CLIENT_ID=$1
PORT=$2

if [ -z "$CLIENT_ID" ] || [ -z "$PORT" ]; then
    echo "Usage: ./deploy-client.sh <client_id> <port>"
    echo "Example: ./deploy-client.sh client2 8002"
    exit 1
fi

echo "Deploying Voice Agent for client: $CLIENT_ID on port: $PORT"

# Create client-specific docker-compose file
cat > docker-compose-${CLIENT_ID}.yml <<EOF
version: '3.8'

services:
  voice-agent-${CLIENT_ID}:
    build: ./backend
    container_name: voice-agent-${CLIENT_ID}
    environment:
      - CLIENT_ID=${CLIENT_ID}
      - DATABASE_URL=postgresql://postgres:postgres@db-${CLIENT_ID}:5432/voice_agent
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - JWT_SECRET=\${JWT_SECRET}
      - PORT=8000
    ports:
      - "${PORT}:8000"
    depends_on:
      - db-${CLIENT_ID}
    networks:
      - ${CLIENT_ID}-network
    restart: unless-stopped

  db-${CLIENT_ID}:
    image: postgres:15-alpine
    container_name: db-${CLIENT_ID}
    environment:
      - POSTGRES_DB=voice_agent
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - ${CLIENT_ID}-db-data:/var/lib/postgresql/data
    networks:
      - ${CLIENT_ID}-network
    restart: unless-stopped

volumes:
  ${CLIENT_ID}-db-data:

networks:
  ${CLIENT_ID}-network:
    driver: bridge
EOF

# Deploy
docker-compose -f docker-compose-${CLIENT_ID}.yml up -d

echo "✅ Client ${CLIENT_ID} deployed successfully!"
echo "API URL: http://localhost:${PORT}/api"
echo "Widget URL: http://localhost:${PORT}/voice-agent-widget.js"
