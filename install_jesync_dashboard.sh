#!/bin/bash

set -e

echo "🚀 Installing Jesync Dashboard..."

# 1. Update system and install dependencies
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git curl nginx

# 2. Clone the repo
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .

# 3. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install python-dotenv

# 4. Create .env file
cat <<EOF > .env
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF
echo "✅ .env created with a secure secret key."

# 5. Create backup directory
sudo mkdir -p /opt/jesyncbak
sudo chown -R $USER:$USER /opt/jesyncbak

# 6. Create systemd service file
sudo tee /etc/systemd/system/jesync_dashboard.service > /dev/null <<EOF
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
EOF

# 7. Enable & start the service
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl restart jesync_dashboard

echo "✅ Jesync Dashboard installed and running at http://<your-ip>:5000"
