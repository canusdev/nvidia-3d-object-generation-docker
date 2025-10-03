#!/bin/bash

#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

echo "=========================================="
echo "Chat-to-3D All-in-One Docker Installation"
echo "=========================================="
echo ""

# Check Docker
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_success "Docker is installed"

# Check Docker Compose
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_success "Docker Compose is installed"

# Check NVIDIA Docker runtime
if ! docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    print_error "NVIDIA Docker runtime is not properly configured"
    echo "Visit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi
print_success "NVIDIA Docker runtime is configured"

# Setup .env file
echo ""
echo "Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    print_warning ".env file created from .env.example"
    echo ""
    echo "Note: If you want to use Llama models, you need a Hugging Face token."
    echo "Get it from: https://huggingface.co/settings/tokens"
    echo ""
    read -p "Enter your Hugging Face token (or press Enter to skip): " HF_TOKEN
    if [ ! -z "$HF_TOKEN" ]; then
        sed -i "s/your_huggingface_token_here/$HF_TOKEN/" .env
        print_success "Hugging Face token saved"
    else
        print_warning "Skipping Hugging Face token (will use fallback models)"
    fi
else
    print_success ".env file already exists"
fi

# Create directories
echo ""
echo "Creating volume directories..."
mkdir -p volumes/assets/images volumes/assets/models
mkdir -p volumes/trellis/assets volumes/trellis/prompts volumes/trellis/scene
mkdir -p volumes/logs/supervisor volumes/logs/app
print_success "Volume directories created"

echo ""
echo "Directory structure:"
echo "  ./volumes/assets/        - Generated images and 3D models"
echo "  ./volumes/trellis/       - Scene data and configurations"
echo "  ./volumes/logs/          - Application and service logs"

# Build and start
echo ""
echo "=========================================="
echo "Building and starting container..."
echo "=========================================="
echo "This may take 30-60 minutes on first build..."
echo "Models will be downloaded on first startup (10-30 min)"
echo ""

docker compose build

echo ""
print_success "Build complete!"
echo ""
echo "Starting container..."
docker compose up -d

echo ""
echo "Waiting for services to be ready..."
echo "This may take several minutes..."

# Wait for health check
MAX_ATTEMPTS=60
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if curl -sf http://localhost:7860 > /dev/null 2>&1; then
        echo ""
        print_success "Application is ready!"
        break
    fi
    echo -n "."
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo ""
    print_warning "Timeout waiting for application"
    echo "Models may still be downloading. Check logs with:"
    echo "  docker compose logs -f"
else
    echo ""
    echo "=========================================="
    echo "Installation Complete!"
    echo "=========================================="
    echo ""
    echo "Access the application at: http://localhost:7860"
    echo ""
    echo "Data locations:"
    echo "  - Assets:  ./volumes/assets/"
    echo "  - Scenes:  ./volumes/trellis/"
    echo "  - Logs:    ./volumes/logs/"
    echo ""
    echo "Useful commands:"
    echo "  - View logs:     docker compose logs -f"
    echo "  - Stop:          docker compose down"
    echo "  - Restart:       docker compose restart"
    echo "  - Status:        docker compose ps"
    echo ""
fi
