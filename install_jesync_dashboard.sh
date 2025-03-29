#!/bin/bash

set -e

echo "🔧 Installing Jesync Dashboard..."

# 1. System Requirements
echo "📦 Installing system dependencies..."
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git curl nginx

# 2. Clone Repo
echo "📁 Cloning repository..."
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .

# 3. Python Virtual Environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 4. Install Python Dependencies
echo "📚 Installing Python packages..."
pip install Flask Flask-Login Flask-SQLAlchemy python-dotenv

# 5. Create .env with secure secret key
echo "🔐 Generating secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "FLASK_SECRET_KEY=$SECRET_KEY" > .env

# 6. Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/jesync_dashboard.service > /dev/null <<EOL
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

# 7. Enable and Start the Dashboard
echo "🚀 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl restart jesync_dashboard

echo "✅ Installation complete!"
echo "🌐 Visit the dashboard at: http://<your-server-ip>:5000"
echo "🔐 Default login:"
echo "   Username: admin"
echo "   Password: adminpass"
