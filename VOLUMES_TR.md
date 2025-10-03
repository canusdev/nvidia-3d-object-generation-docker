# 📦 Volume Management Guide

Bu dokümantasyon, All-in-One container'ın volume yapısını ve yönetimini açıklar.

## 📁 Volume Yapısı

```
allinone/
└── volumes/                      # Tüm kalıcı veriler burada
    ├── assets/                   # Üretilen içerik
    │   ├── images/              # Generated images
    │   │   └── *.png           # Image outputs
    │   └── models/              # 3D models
    │       └── *.glb           # GLB format 3D files
    │
    ├── trellis/                 # Application data
    │   ├── assets/             # Trellis output assets
    │   ├── prompts/            # Saved prompts
    │   └── scene/              # Scene configurations
    │
    └── logs/                    # Log files
        ├── supervisor/         # Service logs
        │   ├── supervisord.log
        │   ├── llm-service.out.log
        │   ├── llm-service.err.log
        │   ├── trellis-service.out.log
        │   ├── trellis-service.err.log
        │   ├── gradio-app.out.log
        │   └── gradio-app.err.log
        └── app/                # Application logs
```

## 🔧 Volume Mount Noktaları

### docker-compose.yml İçinde:

```yaml
volumes:
  # Üretilen içerik (images ve 3D models)
  - ./volumes/assets:/app/assets

  # Scene ve generation data
  - ./volumes/trellis:/root/.trellis

  # Model cache'leri (Docker managed)
  - huggingface-cache:/root/.cache/huggingface
  - torch-cache:/root/.cache/torch

  # Log dosyaları
  - ./volumes/logs/supervisor:/var/log/supervisor
  - ./volumes/logs/app:/var/log/app
```

## 📊 Volume Türleri

### 1. Local Bind Mounts (Host'ta Erişilebilir)

**assets/** - Üretilen içerik

- 📍 Host: `./volumes/assets/`
- 🐳 Container: `/app/assets/`
- 📝 İçerik: Generated images, 3D models
- 💾 Boyut: Değişken (kullanıma göre)

**trellis/** - Uygulama verisi

- 📍 Host: `./volumes/trellis/`
- 🐳 Container: `/root/.trellis/`
- 📝 İçerik: Scene data, prompts, configs
- 💾 Boyut: ~100MB - 1GB

**logs/** - Log dosyaları

- 📍 Host: `./volumes/logs/`
- 🐳 Container: `/var/log/`
- 📝 İçerik: Service ve app logları
- 💾 Boyut: ~10MB - 100MB

### 2. Docker Managed Volumes (Docker yönetimi)

**huggingface-cache** - Hugging Face model cache

- 🐳 Container: `/root/.cache/huggingface/`
- 📝 İçerik: Downloaded HF models
- 💾 Boyut: ~5GB - 20GB
- ⚠️ Host'ta direkt erişilemez

**torch-cache** - PyTorch cache

- 🐳 Container: `/root/.cache/torch/`
- 📝 İçerik: PyTorch models ve cache
- 💾 Boyut: ~1GB - 5GB
- ⚠️ Host'ta direkt erişilemez

## 🎯 Kullanım Senaryoları

### Üretilen Dosyalara Erişim

```bash
# Image'lara bak
ls -lh volumes/assets/images/

# 3D modelleri görüntüle
ls -lh volumes/assets/models/

# Bir modeli kopyala
cp volumes/assets/models/output_*.glb ~/Downloads/
```

### Logları İzleme

```bash
# Tüm loglar
tail -f volumes/logs/supervisor/*.log

# Sadece LLM servisi
tail -f volumes/logs/supervisor/llm-service.out.log

# Sadece hatalar
tail -f volumes/logs/supervisor/*err.log
```

### Backup Alma

```bash
# Tüm volumes'u yedekle
tar czf backup-$(date +%Y%m%d).tar.gz volumes/

# Sadece assets'i yedekle
tar czf assets-backup.tar.gz volumes/assets/

# Sadece logs'u yedekle
tar czf logs-backup.tar.gz volumes/logs/
```

### Temizlik

```bash
# Sadece image'leri temizle
rm -rf volumes/assets/images/*

# Sadece modelleri temizle
rm -rf volumes/assets/models/*

# Tüm üretilen içeriği temizle
rm -rf volumes/assets/*

# Logları temizle
rm -rf volumes/logs/supervisor/*.log
rm -rf volumes/logs/app/*.log
```

## 🔄 Model Download (Runtime)

### İlk Başlatma

```bash
docker compose up -d

# Model download loglarını izle
docker compose logs -f | grep -i "download\|model"
```

**Download süresi:** 10-30 dakika (internet hızına bağlı)

### İndirilen Modeller

Container başlatıldığında `download_models.py` çalışır:

1. **Sana Sprint Model** (~2GB)

   - `Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers`
   - Image generation için

2. **NSFW Detector Model** (~500MB)
   - `ezb/NSFW-Prompt-Detector`
   - Content filtering için

**Toplam:** ~2.5GB - 5GB

### Cache Konumu

Modeller cache'lenir:

- Hugging Face: `huggingface-cache` volume
- PyTorch: `torch-cache` volume

Sonraki başlatmalarda yeniden indirilmez!

## 💾 Disk Kullanımı

### Tahmini Boyutlar

```
volumes/
├── assets/          ~1GB - 10GB    (kullanıma göre)
├── trellis/         ~100MB - 1GB
└── logs/            ~10MB - 100MB

Docker Volumes:
├── huggingface-cache  ~5GB - 20GB
└── torch-cache        ~1GB - 5GB

Toplam: ~7GB - 36GB
```

### Disk Kullanımını Kontrol Et

```bash
# Host volumes
du -sh volumes/*

# Docker volumes
docker system df -v

# Container disk kullanımı
docker compose exec chat-to-3d-allinone df -h
```

## 🧹 Temizlik İşlemleri

### Üretilen İçeriği Temizle

```bash
# Sadece dosyaları sil (dizinleri koru)
rm -f volumes/assets/images/*
rm -f volumes/assets/models/*
```

### Logları Temizle

```bash
# Eski logları sil
find volumes/logs/ -name "*.log" -mtime +7 -delete

# Veya tümünü temizle
rm -rf volumes/logs/**/*.log
```

### Tüm Volumes'u Sıfırla

```bash
# Container'ı durdur
docker compose down

# Volumes'u sil
rm -rf volumes/

# Yeniden başlat (dizinler otomatik oluşur)
docker compose up -d
```

### Docker Cache'i Temizle

```bash
# Container'ı durdur
docker compose down -v

# Cache volumes'u sil
docker volume rm allinone_huggingface-cache
docker volume rm allinone_torch-cache

# Yeniden başlat (modeller yeniden indirilir)
docker compose up -d
```

## 🔐 İzinler

### Dosya Sahipliği

Container içinde root olarak çalışır:

- Owner: `root:root`
- Permissions: `755` (dirs), `644` (files)

### Host'tan Erişim

Normal kullanıcı ile erişebilmek için:

```bash
# Sahipliği değiştir
sudo chown -R $USER:$USER volumes/

# Veya tüm izinleri aç (dikkatli kullan!)
sudo chmod -R 777 volumes/
```

## 📤 Export/Import

### Export

```bash
# Tüm veriyi export et
docker compose down
tar czf chat-to-3d-backup.tar.gz volumes/

# Sadece önemli veriyi export et
tar czf assets-backup.tar.gz volumes/assets/ volumes/trellis/
```

### Import

```bash
# Yeni sistemde
cd allinone
tar xzf chat-to-3d-backup.tar.gz

# Container'ı başlat
docker compose up -d
```

## 🔍 Troubleshooting

### Volume mount hataları

```bash
# Dizinleri kontrol et
ls -la volumes/

# Yeniden oluştur
mkdir -p volumes/{assets/{images,models},trellis/{assets,prompts,scene},logs/{supervisor,app}}

# İzinleri düzelt
chmod -R 755 volumes/
```

### Disk dolu

```bash
# Kullanımı kontrol et
df -h

# Eski dosyaları temizle
find volumes/assets/images/ -mtime +30 -delete
find volumes/assets/models/ -mtime +30 -delete

# Docker cache'i temizle
docker system prune -a
```

### Logs çok büyük

```bash
# Log boyutlarını kontrol et
du -sh volumes/logs/*

# Eski logları sil
find volumes/logs/ -name "*.log" -mtime +7 -delete

# Veya rotate et
for log in volumes/logs/**/*.log; do
    if [ -f "$log" ]; then
        mv "$log" "$log.$(date +%Y%m%d)"
        touch "$log"
    fi
done
```

## 📝 Best Practices

1. **Regular Backups**: Önemli assetleri düzenli yedekle
2. **Log Rotation**: Eski logları düzenli temizle
3. **Disk Monitoring**: Disk kullanımını takip et
4. **Selective Cleanup**: Sadece gereksiz dosyaları temizle
5. **Version Control**: Önemli scene'leri git'e commit et

## 🔗 İlgili Komutlar

```bash
# Volume durumunu göster
docker compose ps -a
docker volume ls

# Container içinde dosya sistemi
docker compose exec chat-to-3d-allinone df -h
docker compose exec chat-to-3d-allinone ls -la /app/assets

# Real-time disk kullanımı
watch -n 5 'du -sh volumes/*'

# Log boyutları
du -sh volumes/logs/**/* | sort -h
```

---

Bu dokümantasyon volume yönetimi için kapsamlı bir kılavuzdur.
Daha fazla bilgi için: [README.md](README.md) ve [QUICKSTART.md](QUICKSTART.md)
