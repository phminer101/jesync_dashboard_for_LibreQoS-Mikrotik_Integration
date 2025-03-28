#!/bin/bash

set -e

echo "📦 Installing Jesync Dashboard..."

# 1. Update and install dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl

# 2. Set up directory
DASH_DIR="/opt/libreqos/src/jesync_dashboard"
if [ -d "$DASH_DIR" ]; then
    echo "⚠️ $DASH_DIR already exists. Skipping clone..."
else
    sudo mkdir -p /opt/libreqos/src
    cd /opt/libreqos/src
    echo "📥 Cloning dashboard repo..."
    sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
    sudo chown -R $USER:$USER "$DASH_DIR"
fi

cd "$DASH_DIR"

# 3. Create virtual environment
echo "🐍 Setting up Python venv..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Python packages
echo "📦 Installing Python packages..."
pip install Flask Flask-Login Flask-SQLAlchemy

# 5. Create systemd service
echo "⚙️ Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/jesync_dashboard.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Jesync Dashboard Web UI
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$DASH_DIR
Environment=PATH=$DASH_DIR/venv/bin
ExecStart=$DASH_DIR/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable and start service
echo "🚀 Starting Jesync Dashboard service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl start jesync_dashboard

echo "✅ Installation complete!"
echo ""
echo "🌐 Access the dashboard at: http://<your-server-ip>:5000"
echo "🔐 Default login: admin / adminpass"
echo ""
echo "📎 To manage the service: sudo systemctl status|restart|stop jesync_dashboard"
