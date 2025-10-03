#!/bin/bash

#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

set -e

echo "=========================================="
echo "Starting Chat-to-3D All-in-One Container"
echo "=========================================="
echo ""

# Activate conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate trellis

# Create necessary directories (if not already present from volumes)
echo "Setting up directories..."
mkdir -p /root/.trellis/assets /root/.trellis/prompts /root/.trellis/scene
mkdir -p /app/assets/images /app/assets/models
mkdir -p /var/log/supervisor /var/log/app

# Download models at startup (runtime download)
echo ""
echo "=========================================="
echo "Downloading required models..."
echo "This may take 10-30 minutes on first run"
echo "=========================================="
echo ""
python /app/download_models.py || echo "⚠ Model download failed, will retry on demand"

echo ""
echo "✓ Initialization complete!"
echo "Starting supervisor to manage services..."
echo ""
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
