#!/bin/bash
set -e

echo "=================================================="
echo "🚀 6 in 1 Video Downloader Bots - VPS O'rnatish"
echo "=================================================="

# Update system packages
echo "📦 Tizim paketlari yangilanmoqda..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-pip python3-venv ffmpeg git curl

APP_DIR="/root/anvarsave-bot"

# Clone or pull latest code
if [ -d "$APP_DIR" ]; then
    echo "🔄 Loyiha yangilanmoqda..."
    cd "$APP_DIR"
    git fetch origin main
    git reset --hard origin/main
else
    echo "📥 Loyiha yuklab olinmoqda..."
    git clone https://github.com/ahmadulloh/anvarsave-bot.git "$APP_DIR"
    cd "$APP_DIR"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Python virtual muhit yaratilmoqda..."
    python3 -m venv venv
fi

# Install requirements
echo "📚 Kutubxonalar o'rnatilmoqda..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Ensure downloads directory exists
mkdir -p downloads

# Create systemd service
SERVICE_FILE="/etc/systemd/system/savebots.service"
echo "⚙️ Systemd service yaratilmoqda: $SERVICE_FILE..."

cat << 'EOF' > "$SERVICE_FILE"
[Unit]
Description=6-in-1 Multi Telegram Video Downloader Bots
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/anvarsave-bot
ExecStart=/root/anvarsave-bot/venv/bin/python bot.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Reload and restart service
systemctl daemon-reload
systemctl enable savebots
systemctl restart savebots

echo "=================================================="
echo "✅ Barcha botlar muvaffaqiyatli ishga tushirildi!"
echo "📊 Holatni tekshirish uchun: systemctl status savebots"
echo "📜 Loglarni ko'rish uchun:   journalctl -u savebots -f"
echo "=================================================="
