# 🚀 Chat-to-3D All-in-One Docker

**All services in a single Docker container!**

This solution runs all components of the Chat-to-3D project (LLM, TRELLIS 3D generation, and Gradio UI) in a single container.

> **Original Project**: [NVIDIA-AI-Blueprints/3d-object-generation](https://github.com/NVIDIA-AI-Blueprints/3d-object-generation)  
> **This Repository**: Dockerized all-in-one version for easy deployment

## 🌟 Features

- ✅ **Single Container**: All services in one container
- ✅ **Simple Setup**: Just run `./install.sh`
- ✅ **Lower Resources**: Local Python instead of NIM containers
- ✅ **Supervisor**: All services managed automatically
- ✅ **GPU Acceleration**: Fast execution with CUDA support

## 🎯 NIM Containers vs All-in-One

| Feature         | NIM Containers | All-in-One     |
| --------------- | -------------- | -------------- |
| Container Count | 3 separate     | 1 single       |
| Memory Usage    | ~20-30GB       | ~10-15GB       |
| Setup Time      | 60-120 minutes | 30-60 minutes  |
| NGC API Key     | Required       | Not required   |
| Startup Time    | 5-10 minutes   | 2-3 minutes    |
| Management      | Docker Compose | Docker Compose |

## 📋 Requirements

- Docker 20.10+
- Docker Compose v2.0+
- NVIDIA Container Toolkit
- NVIDIA GPU (16GB+ VRAM recommended)
- 50GB+ disk space

### NVIDIA Container Toolkit Installation

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## 🚀 Quick Start

### 1. Installation

```bash
cd allinone
chmod +x install.sh
./install.sh
```

### 2. Usage

Open in your browser: http://localhost:7860

## 📦 Manual Installation

```bash
# Create .env file (optional)
cp .env.example .env
nano .env  # Add HF_TOKEN (optional)

# Build and start container
docker compose build
docker compose up -d

# Follow logs
docker compose logs -f
```

## 🔧 Management Commands

```bash
# Start container
docker compose up -d

# Stop container
docker compose down

# View logs
docker compose logs -f

# View individual service logs
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/llm-service.out.log
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/trellis-service.out.log
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/gradio-app.out.log

# Enter container
docker compose exec chat-to-3d-allinone bash

# Restart services (inside container)
docker compose exec chat-to-3d-allinone supervisorctl restart all

# Restart container
docker compose restart

# Remove all data
docker compose down -v
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     All-in-One Docker Container         │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │        Supervisor                  │ │
│  └────────┬──────────┬────────────────┘ │
│           │          │          │        │
│  ┌────────▼───┐ ┌────▼─────┐ ┌─▼──────┐ │
│  │ LLM Service│ │ TRELLIS  │ │ Gradio │ │
│  │ Port: 19002│ │Port: 8000│ │Port:   │ │
│  │ (internal) │ │(internal)│ │7860    │ │
│  └────────────┘ └──────────┘ └────────┘ │
│                                          │
└─────────────────────────────────────────┘
           │
           └─── Port 7860 (Exposed)
```

### Service Details

**Supervisor**: Manages all services

- Automatically starts services
- Restarts on failure
- Manages logs

**LLM Service** (Port 19002, internal):

- Transformers-based LLM
- OpenAI-compatible API
- Llama 3.1 or Llama 2 fallback

**TRELLIS Service** (Port 8000, internal):

- 3D model generation
- Image-to-3D pipeline
- GLB format export

**Gradio App** (Port 7860, exposed):

- Web UI
- Uses both services
- User interface

## 🔍 Troubleshooting

### Container won't start?

```bash
# Check logs
docker compose logs -f

# Specific service logs
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/llm-service.err.log
```

### GPU not detected?

```bash
# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi

# Check GPU inside container
docker compose exec chat-to-3d-allinone nvidia-smi
```

### Model loading errors?

Hugging Face token may be required (for Llama models):

1. Get token from https://huggingface.co/settings/tokens
2. Add to `.env` file: `HF_TOKEN=your_token_here`
3. Restart container: `docker compose restart`

### Out of memory?

Increase `shm_size` in `docker-compose.yml`:

```yaml
shm_size: 32gb # Default: 16gb
```

### Services can't find each other?

Check service status inside container:

```bash
docker compose exec chat-to-3d-allinone supervisorctl status
```

Restart services:

```bash
docker compose exec chat-to-3d-allinone supervisorctl restart all
```

## 📊 Performance

- **First Startup**: 30-60 minutes (model download)
- **Subsequent Startups**: 2-3 minutes
- **GPU Memory**: 10-15GB
- **Disk Usage**: ~50GB (with models)

## 🔄 Updating

```bash
# Pull latest code
git pull

# Rebuild container
docker compose build --no-cache

# Restart
docker compose up -d
```

## 🆚 Comparison with Main Docker Compose

### All-in-One Advantages:

- ✅ Simpler structure
- ✅ Lower memory usage
- ✅ Faster startup
- ✅ No NGC API key needed
- ✅ Easier to debug

### Main Docker Compose Advantages:

- ✅ NVIDIA NIM optimizations
- ✅ Better performance (in some cases)
- ✅ Services can scale independently
- ✅ Official NVIDIA images

## 📝 Notes

- Models are downloaded on first run
- Models are cached, subsequent startups are fast
- All data is stored in Docker volumes
- Don't commit your `.env` file to git

## 🐛 Bug Reporting

If you encounter issues, please collect the following information:

```bash
# System information
docker version
docker compose version
nvidia-smi

# Container logs
docker compose logs > logs.txt

# Supervisor status
docker compose exec chat-to-3d-allinone supervisorctl status
```

## 📄 License

Apache 2.0 License - See LICENSE file for details.

---

**Ready to start?** Begin now: `./install.sh` 🚀
