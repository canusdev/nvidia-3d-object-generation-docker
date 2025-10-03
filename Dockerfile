#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH=/opt/conda/bin:$PATH \
    CHAT_TO_3D_PATH=/app \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    build-essential \
    ca-certificates \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    /opt/conda/bin/conda init bash && \
    /opt/conda/bin/conda config --set always_yes yes --set changeps1 no

# Accept Anaconda Terms of Service
RUN /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
    /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2

# Create conda environment
RUN /opt/conda/bin/conda create -n trellis python=3.11.9 -y && \
    /opt/conda/bin/conda clean -afy

# Set working directory
WORKDIR /tmp

# Clone the repository
ARG REPO_URL=https://github.com/NVIDIA-AI-Blueprints/3d-object-generation.git
ARG REPO_BRANCH=main
RUN git clone --depth 1 --branch ${REPO_BRANCH} ${REPO_URL} repo && \
    mv repo /app && \
    cd /app && \
    rm -rf .git

# Set working directory to app
WORKDIR /app

# Copy extra requirements
COPY requirements-extra.txt ./

# Install Python packages in conda environment
RUN /opt/conda/bin/conda run -n trellis pip install --no-cache-dir --upgrade pip wheel && \
    /opt/conda/bin/conda run -n trellis pip install --no-cache-dir setuptools==75.8.2 && \
    /opt/conda/bin/conda run -n trellis pip install --no-cache-dir -r requirements-torch.txt && \
    /opt/conda/bin/conda run -n trellis pip install --no-cache-dir -r requirements.txt && \
    /opt/conda/bin/conda run -n trellis pip install --no-cache-dir -r requirements-extra.txt

# Copy and apply patches (local services and configurations)
COPY nim_llm/run_llama_local.py /app/nim_llm/
COPY nim_trellis/run_trellis_local.py /app/nim_trellis/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start.sh /app/start.sh

# Make scripts executable
RUN chmod +x /app/start.sh && \
    chmod +x /app/nim_llm/run_llama_local.py && \
    chmod +x /app/nim_trellis/run_trellis_local.py

# Create necessary directories (will be mounted as volumes)
RUN mkdir -p /root/.trellis/assets /root/.trellis/prompts /root/.trellis/scene && \
    mkdir -p /app/assets/images /app/assets/models && \
    mkdir -p /var/log/supervisor /var/log/app

# Create volume mount points
VOLUME ["/app/assets", "/root/.trellis", "/var/log/supervisor", "/var/log/app"]

# Expose ports
# 7860 - Gradio UI (exposed)
# 19002 - LLM Service (internal)
# 8000 - TRELLIS Service (internal)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:7860 || exit 1

# Use supervisor to manage all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
