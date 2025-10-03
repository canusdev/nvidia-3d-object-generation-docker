# ⚡ Chat-to-3D All-in-One - Hızlı Başlangıç

Tek container'da tüm servisler! En basit ve hızlı kurulum.

## 🎯 3 Adımda Başlat

### 1️⃣ Gereksinimleri Kontrol Et

```bash
# Docker ve NVIDIA runtime var mı?
docker --version
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

Yoksa: [README.md](README.md#-gereksinimler) kurulum talimatları

### 2️⃣ Kurulum

```bash
cd allinone
./install.sh
```

**Not:** İlk başlatmada modeller indirilir (10-30 dakika)

### 3️⃣ Kullan!

Tarayıcıda aç: **http://localhost:7860**

## 📂 Verileriniz

Tüm veriler `./volumes/` klasöründe:

```
volumes/
├── assets/          # Üretilen görseller ve 3D modeller
│   ├── images/      # Generated images (.png)
│   └── models/      # 3D models (.glb)
├── trellis/         # Scene data ve config
│   ├── assets/
│   ├── prompts/
│   └── scene/
└── logs/            # Uygulama logları
    ├── supervisor/  # Service logs
    └── app/         # App logs
```

## 🚀 İşte Bu Kadar!

---

## 📋 Temel Komutlar

```bash
# Başlat
docker compose up -d

# Durdur
docker compose down

# Logları izle
docker compose logs -f

# Model download loglarını izle
docker compose logs -f | grep -i "download\|model"

# Yeniden başlat
docker compose restart

# Durum kontrolü
docker compose ps
```

## 🔍 Log Görüntüleme

```bash
# Tüm servisler
docker compose logs -f

# Sadece LLM servisi
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/llm-service.out.log

# Sadece TRELLIS servisi
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/trellis-service.out.log

# Sadece Gradio app
docker compose exec chat-to-3d-allinone tail -f /var/log/supervisor/gradio-app.out.log
```

## ⚙️ İleri Düzey

### Container İçine Gir

```bash
docker compose exec chat-to-3d-allinone bash
```

### Servisleri Yönet (Container İçinde)

```bash
# Servis durumu
supervisorctl status

# Servisi yeniden başlat
supervisorctl restart llm-service
supervisorctl restart trellis-service
supervisorctl restart gradio-app

# Tüm servisleri yeniden başlat
supervisorctl restart all

# Servisi durdur/başlat
supervisorctl stop llm-service
supervisorctl start llm-service
```

### GPU Kullanımını İzle

```bash
# Host'ta
watch -n 1 nvidia-smi

# Container içinde
docker compose exec chat-to-3d-allinone watch -n 1 nvidia-smi
```

## 🆚 Hangisini Seçmeli?

### All-in-One (Bu Klasör)

✅ **Kullan Eğer:**

- Basit kurulum istiyorsun
- Tek GPU'n var
- NGC API key istemiyorsun
- Hızlı prototipleme yapıyorsun
- Düşük bellek kullanımı önemli

### Ana Docker Compose (Üst Klasör)

✅ **Kullan Eğer:**

- Production ortamı
- Servisler ayrı scale edilecek
- NVIDIA NIM optimizasyonları önemli
- Birden fazla GPU var
- NGC API key kullanabiliyorsun

## 🐛 Sorun mu Var?

### 1. Container başlamıyor

```bash
docker compose logs -f
```

### 2. GPU tanınmıyor

```bash
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

### 3. Servis hataları

```bash
# Container içinde servis durumunu kontrol et
docker compose exec chat-to-3d-allinone supervisorctl status

# Servisi yeniden başlat
docker compose exec chat-to-3d-allinone supervisorctl restart all
```

### 4. Bellek problemi

`docker-compose.yml` içinde `shm_size: 32gb` yap

### 5. Model yüklenmiyor

`.env` dosyasına `HF_TOKEN` ekle ve restart et

## 📖 Daha Fazla Bilgi

Detaylı dokümantasyon: [README.md](README.md)

---

**Sorun mu var?** Logları kontrol et: `docker compose logs -f`

**Çalıştı mı?** 🎉 http://localhost:7860 adresini ziyaret et!
