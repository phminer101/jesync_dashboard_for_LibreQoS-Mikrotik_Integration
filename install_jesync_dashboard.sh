#!/bin/bash

# Jesync Dashboard Auto Installer Script (Updated with Backup Support)

set -e

echo "🚀 Installing Jesync Dashboard..."

# 1. Update & install required packages
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl nginx

# 2. Clone repository
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .

# 3. Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install python-dotenv

# 4. Create /opt/jesyncbak directory for backups
sudo mkdir -p /opt/jesyncbak
sudo chown $USER:$USER /opt/jesyncbak

# 5. Create .env with secure secret key
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env

# 6. Set up systemd service
SERVICE_FILE=/etc/systemd/system/jesync_dashboard.service
sudo tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=Jesync Dashboard Web UI
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/libreqos/src/jesync_dashboard
Environment="PATH=/opt/libreqos/src/jesync_dashboard/venv/bin"
ExecStart=/opt/libreqos/src/jesync_dashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 7. Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl restart jesync_dashboard

echo "✅ Jesync Dashboard installed and running at http://<your-server-ip>:5000"
