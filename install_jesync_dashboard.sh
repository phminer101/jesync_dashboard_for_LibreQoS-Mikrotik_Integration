#!/bin/bash
# =========================================
# 📦 JESYNC UI TOOL DASHBOARD INSTALLER
# =========================================

set -e

echo "🔧 Updating packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl nginx dos2unix

echo "📁 Cloning Dashboard..."
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .

echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🛠️ Setting up .env file..."
cat <<EOF > .env
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF

echo "🗂️ Installing systemd service..."
sudo tee /etc/systemd/system/jesync_dashboard.service > /dev/null <<EOL
[Unit]
Description=Jesync Dashboard Web UI
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/libreqos/src/jesync_dashboard
Environment="PATH=/opt/libreqos/src/jesync_dashboard/venv/bin"
EnvironmentFile=/opt/libreqos/src/jesync_dashboard/.env
ExecStart=/opt/libreqos/src/jesync_dashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

echo "✅ Reloading and enabling service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl start jesync_dashboard

echo "🎉 Installation complete!"
echo "🌐 Visit: http://<your-server-ip>:5000"
