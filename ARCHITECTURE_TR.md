# Chat-to-3D All-in-One Docker - Dosya Yapısı

Bu dokümantasyon, all-in-one container çözümü için oluşturulan dosyaları açıklar.

## 📁 Dizin Yapısı

```
allinone/
├── Dockerfile                  # All-in-one container tanımı
├── docker-compose.yml          # Tek container orchestration
├── supervisord.conf           # Servis yönetimi (3 servis)
├── start.sh                   # Container başlangıç scripti
├── install.sh                 # Otomatik kurulum scripti
├── requirements-extra.txt     # Ekstra Python bağımlılıkları
├── .env.example              # Örnek ortam değişkenleri
├── .dockerignore             # Docker build ignore
├── .gitignore                # Git ignore
├── README.md                 # Detaylı dokümantasyon
└── QUICKSTART.md             # Hızlı başlangıç kılavuzu

Ana dizin (../):
├── nim_llm/
│   └── run_llama_local.py    # Local LLM servisi (Transformers)
└── nim_trellis/
    └── run_trellis_local.py  # Local TRELLIS servisi (Python)
```

## 📄 Dosya Açıklamaları

### Dockerfile

**Amaç:** Tek container imajını oluşturur

**İçerik:**

- CUDA 12.8.1 base
- Miniconda kurulumu
- Python 3.11.9 conda ortamı
- Tüm bağımlılıkları yükler
- Supervisor kurulumu
- Model indirme (build time)
- Port 7860 expose

**Özellikler:**

- Multi-stage değil (all-in-one)
- Supervisor ile servis yönetimi
- GPU desteği
- Health check dahil

### docker-compose.yml

**Amaç:** Container'ı başlatır ve yapılandırır

**Servis:** `chat-to-3d-allinone`

- Single service tanımı
- GPU reservation
- Volume mount'ları
- Environment variables
- Health check
- Restart policy

**Volume'lar:**

- `trellis-data`: Uygulama verileri
- `huggingface-cache`: HF model cache
- `torch-cache`: PyTorch cache

### supervisord.conf

**Amaç:** Container içinde 3 servisi yönetir

**Servisler:**

1. **llm-service** (Priority 1)

   - `/app/nim_llm/run_llama_local.py`
   - Port: 19002 (internal)
   - Auto-restart

2. **trellis-service** (Priority 2)

   - `/app/nim_trellis/run_trellis_local.py`
   - Port: 8000 (internal)
   - Auto-restart

3. **gradio-app** (Priority 3)
   - `/app/app.py`
   - Port: 7860 (exposed)
   - Auto-restart
   - 30s start delay

**Log Yönetimi:**

- `/var/log/supervisor/`
- Her servis için ayrı log dosyaları
- stdout ve stderr ayrı

### start.sh

**Amaç:** Container başlangıç işlemleri

**İşlemler:**

1. Conda ortamını aktive et
2. Model'leri kontrol et/indir
3. Dizinleri oluştur
4. Supervisor'u başlat

### install.sh

**Amaç:** Otomatik kurulum ve başlatma

**Adımlar:**

1. Gereksinimleri kontrol et (Docker, GPU, etc.)
2. `.env` dosyası oluştur
3. HF token al (opsiyonel)
4. Dizinleri oluştur
5. Container'ı build et
6. Container'ı başlat
7. Health check yap
8. Sonuç bildir

### requirements-extra.txt

**Amaç:** All-in-one için ekstra bağımlılıklar

**Paketler:**

- `fastapi`: REST API framework
- `uvicorn`: ASGI server

**Neden ayrı:**
Ana requirements'ta yok, sadece local servisler için gerekli

### .env.example

**Amaç:** Ortam değişkenleri şablonu

**Değişkenler:**

- `HF_TOKEN`: Hugging Face token (Llama için)
- `GRADIO_SERVER_NAME`: Gradio host
- `GRADIO_SERVER_PORT`: Gradio port
- `CUDA_VISIBLE_DEVICES`: GPU seçimi

### run_llama_local.py

**Amaç:** Local LLM servisi (NIM replacement)

**Özellikler:**

- FastAPI REST API
- OpenAI-compatible endpoints
- Transformers backend
- Llama 3.1 veya Llama 2 fallback
- GPU auto-detection
- Health check endpoints

**Endpoints:**

- `GET /v1/health/ready`: Hazır mı?
- `GET /v1/health/live`: Çalışıyor mu?
- `POST /v1/chat/completions`: Chat API
- `GET /v1/models`: Model listesi

### run_trellis_local.py

**Amaç:** Local TRELLIS 3D generation servisi

**Özellikler:**

- FastAPI REST API
- TRELLIS pipeline
- Image-to-3D conversion
- GLB export
- Content filtering
- GPU acceleration

**Endpoints:**

- `GET /v1/health/ready`: Hazır mı?
- `GET /v1/health/live`: Çalışıyor mu?
- `POST /v1/infer`: 3D generation

## 🔄 İş Akışı

### Build Time (Dockerfile)

```
1. Base image (CUDA + Ubuntu)
2. System dependencies
3. Miniconda install
4. Conda environment create
5. Python packages install
6. App files copy
7. Model download (optional)
8. Directory setup
9. Supervisor config
10. Permissions
```

### Runtime (supervisord.conf)

```
Container Start
    ↓
start.sh
    ↓
Supervisor Start
    ↓
├─→ llm-service (Priority 1)
│   └─ run_llama_local.py → Port 19002
│
├─→ trellis-service (Priority 2)
│   └─ run_trellis_local.py → Port 8000
│
└─→ gradio-app (Priority 3)
    └─ app.py → Port 7860
```

### User Request Flow

```
Browser (Port 7860)
    ↓
Gradio App
    ↓
├─→ LLM Service (Port 19002)
│   └─ Transformers → LLM response
│
└─→ TRELLIS Service (Port 8000)
    └─ TRELLIS Pipeline → 3D GLB
```

## 🔧 Servis Yönetimi

### Supervisor Commands (Container içinde)

```bash
# Durum kontrol
supervisorctl status

# Servis başlat/durdur
supervisorctl start llm-service
supervisorctl stop trellis-service
supervisorctl restart gradio-app

# Tüm servisleri yeniden başlat
supervisorctl restart all

# Logları izle
supervisorctl tail -f llm-service
supervisorctl tail -f trellis-service stdout
```

### Docker Commands (Host'ta)

```bash
# Container başlat
docker compose up -d

# Logları izle
docker compose logs -f

# Container içine gir
docker compose exec chat-to-3d-allinone bash

# Servis durumu (container içinde)
docker compose exec chat-to-3d-allinone supervisorctl status

# Container'ı yeniden başlat
docker compose restart
```

## 📊 Resource Usage

### Build Time

- Disk: ~30GB (layers + cache)
- Time: 30-60 dakika (ilk defa)
- Network: ~10GB (downloads)

### Runtime

- GPU VRAM: 10-15GB
- RAM: 8-16GB
- Disk: 50GB (models + cache)
- CPU: 4+ cores önerilir

## 🔐 Güvenlik

### Port Exposure

- **7860**: Public (Gradio UI)
- **19002**: Internal (LLM service)
- **8000**: Internal (TRELLIS service)

### Credentials

- HF_TOKEN: `.env` dosyasında
- `.env` git'e commit edilmez (.gitignore)

## 🐛 Debug

### Log Locations

```
/var/log/supervisor/
├── supervisord.log              # Ana log
├── llm-service.out.log          # LLM stdout
├── llm-service.err.log          # LLM stderr
├── trellis-service.out.log      # TRELLIS stdout
├── trellis-service.err.log      # TRELLIS stderr
├── gradio-app.out.log           # Gradio stdout
└── gradio-app.err.log           # Gradio stderr
```

### Common Issues

**Model yükleme hatası:**

- Log: `llm-service.err.log`
- Çözüm: HF_TOKEN ekle

**GPU tanınmıyor:**

- Log: `trellis-service.err.log`
- Çözüm: NVIDIA runtime kontrol

**Port conflict:**

- Log: `gradio-app.err.log`
- Çözüm: Port değiştir

## 📝 Geliştirme

### Yeni Servis Eklemek

1. `supervisord.conf`'a ekle:

```ini
[program:yeni-servis]
command=/opt/conda/bin/conda run -n trellis python /app/yeni_servis.py
directory=/app
autostart=true
autorestart=true
```

2. Container'ı rebuild et:

```bash
docker compose build --no-cache
docker compose up -d
```

### Dependency Eklemek

1. `requirements-extra.txt`'e ekle
2. Rebuild:

```bash
docker compose build --no-cache
```

## 🔄 Güncelleme

```bash
# Kodu güncelle
git pull

# Rebuild (no cache)
docker compose build --no-cache

# Restart
docker compose down
docker compose up -d
```

## 📚 İlgili Dosyalar

- Ana Docker Compose: `../docker-compose.yml`
- Ana Dockerfile: `../Dockerfile`
- Original install.bat: `../install.bat`
- Config: `../config.py`

---

Bu dokümantasyon all-in-one çözümünün teknik detaylarını içerir.
Kullanıcı dokümantasyonu için: `README.md` ve `QUICKSTART.md`
