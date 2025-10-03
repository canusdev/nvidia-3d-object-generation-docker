# 🚀 Chat-to-3D All-in-One Docker

**Tek bir Docker container'da tüm servisler!**

Bu çözüm, Chat-to-3D projesinin tüm bileşenlerini (LLM, TRELLIS 3D generation, ve Gradio UI) tek bir container içinde çalıştırır.

## 🌟 Özellikler

- ✅ **Tek Container**: Tüm servisler tek container'da
- ✅ **Basit Kurulum**: Sadece `./install.sh`
- ✅ **Düşük Kaynak**: NIM container'ları yerine yerel Python
- ✅ **Supervisor**: Tüm servisler otomatik yönetilir
- ✅ **GPU Hızlandırma**: CUDA desteği ile hızlı çalışma

## 🎯 NIM Container vs All-in-One

| Özellik          | NIM Containers | All-in-One     |
| ---------------- | -------------- | -------------- |
| Container Sayısı | 3 ayrı         | 1 tek          |
| Bellek Kullanımı | ~20-30GB       | ~10-15GB       |
| Kurulum Süresi   | 60-120 dakika  | 30-60 dakika   |
| NGC API Key      | Gerekli        | Gerekmez       |
| Başlatma Süresi  | 5-10 dakika    | 2-3 dakika     |
| Yönetim          | Docker Compose | Docker Compose |

## 📋 Gereksinimler

- Docker 20.10+
- Docker Compose v2.0+
- NVIDIA Container Toolkit
- NVIDIA GPU (16GB+ VRAM önerilir)
- 50GB+ disk alanı

### NVIDIA Container Toolkit Kurulumu

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

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
cd allinone
chmod +x install.sh
./install.sh
```

### 2. Kullanım

Tarayıcınızda açın: http://localhost:7860

## 📦 Manuel Kurulum

```bash
# .env dosyasını oluştur (opsiyonel)
cp .env.example .env
nano .env  # HF_TOKEN ekle (opsiyonel)

# Container'ı build et ve başlat
docker compose build
docker compose up -d

# Logları izle
docker compose logs -f
```

## 🔧 Yönetim Komutları

```bash
# Container'ı başlat
docker compose up -d

# Container'ı durdur
docker compose down

# Logları görüntüle
docker compose logs -f

# Servis loglarını ayrı ayrı görüntüle
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/llm-service.out.log
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/trellis-service.out.log
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/gradio-app.out.log

# Container içine gir
docker compose exec chat-to-3d-allinone bash

# Servisleri yeniden başlat (container içinde)
docker compose exec chat-to-3d-allinone supervisorctl restart all

# Container'ı yeniden başlat
docker compose restart

# Tüm verileri sil
docker compose down -v
```

## 🏗️ Mimari

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

### Servis Detayları

**Supervisor**: Tüm servisleri yönetir

- Servisleri otomatik başlatır
- Çökme durumunda yeniden başlatır
- Log yönetimi yapar

**LLM Service** (Port 19002, internal):

- Transformers tabanlı LLM
- OpenAI-compatible API
- Llama 3.1 veya Llama 2 fallback

**TRELLIS Service** (Port 8000, internal):

- 3D model generation
- Image-to-3D pipeline
- GLB format export

**Gradio App** (Port 7860, exposed):

- Web UI
- İki servisi kullanır
- Kullanıcı arayüzü

## 🔍 Sorun Giderme

### Container başlamıyor?

```bash
# Logları kontrol et
docker compose logs -f

# Belirli bir servisin logları
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/llm-service.err.log
```

### GPU tanınmıyor?

```bash
# GPU erişimini test et
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi

# Container içinde GPU kontrolü
docker compose exec chat-to-3d-allinone nvidia-smi
```

### Model yükleme hataları?

Hugging Face token gerekli olabilir (Llama modelleri için):

1. https://huggingface.co/settings/tokens adresinden token alın
2. `.env` dosyasına ekleyin: `HF_TOKEN=your_token_here`
3. Container'ı yeniden başlatın: `docker compose restart`

### Bellek yetersizliği?

`docker-compose.yml` dosyasında `shm_size` değerini artırın:

```yaml
shm_size: 32gb # Varsayılan: 16gb
```

### Servisler birbirini bulamıyor?

Container içinde servislerin durumunu kontrol edin:

```bash
docker compose exec chat-to-3d-allinone supervisorctl status
```

Servisleri yeniden başlatın:

```bash
docker compose exec chat-to-3d-allinone supervisorctl restart all
```

## 📊 Performans

- **İlk Başlatma**: 30-60 dakika (model indirme)
- **Sonraki Başlatmalar**: 2-3 dakika
- **GPU Belleği**: 10-15GB
- **Disk Kullanımı**: ~50GB (modellerle)

## 🔄 Güncelleme

```bash
# En son kodu çek
git pull

# Container'ı yeniden build et
docker compose build --no-cache

# Yeniden başlat
docker compose up -d
```

## 🆚 Ana Docker Compose ile Karşılaştırma

### All-in-One Avantajları:

- ✅ Daha basit yapı
- ✅ Daha az bellek kullanımı
- ✅ Daha hızlı başlatma
- ✅ NGC API key gerekmez
- ✅ Daha kolay debug

### Ana Docker Compose Avantajları:

- ✅ NVIDIA NIM optimizasyonları
- ✅ Daha iyi performans (bazı durumlarda)
- ✅ Servisler bağımsız ölçeklenebilir
- ✅ Resmi NVIDIA imajları

## 📝 Notlar

- İlk çalıştırmada modeller indirilir
- Modeller cache'lenir, sonraki başlatmalar hızlıdır
- Tüm veriler Docker volume'larında saklanır
- `.env` dosyanızı git'e commit etmeyin

## 🐛 Sorun Bildirme

Sorun yaşarsanız, lütfen şu bilgileri toplayın:

```bash
# Sistem bilgileri
docker version
docker compose version
nvidia-smi

# Container logları
docker compose logs > logs.txt

# Supervisor durumu
docker compose exec chat-to-3d-allinone supervisorctl status
```

## 📄 Lisans

Apache 2.0 License - Detaylar için LICENSE dosyasına bakınız.

---

**Hazır mısınız?** Hemen başlayın: `./install.sh` 🚀
