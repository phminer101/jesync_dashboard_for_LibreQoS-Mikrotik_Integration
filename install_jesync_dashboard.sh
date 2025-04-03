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

if [ ! -d jesync_dashboard ]; then
  sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
fi

cd jesync_dashboard
sudo chown -R "$USER:$USER" .

echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🛠️ Creating .env with secure SECRET_KEY..."
cat <<EOF > .env
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF

echo "📝 Creating updatejesync.sh script..."
cat <<'EOL' > updatejesync.sh
#!/bin/bash
set -e
REPO_DIR="/opt/libreqos/src/jesync_dashboard"
BACKUP_DIR="/opt/jesyncbak/autoupdate_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$REPO_DIR/update.log"

echo "📦 Starting Jesync Dashboard update..." | tee -a "$LOG_FILE"
echo "🕒 $(date)" | tee -a "$LOG_FILE"

echo "📁 Backing up current dashboard to $BACKUP_DIR" | tee -a "$LOG_FILE"
mkdir -p "$BACKUP_DIR"
cp -r "$REPO_DIR"/* "$BACKUP_DIR"

cd "$REPO_DIR"
git reset --hard
git pull origin main | tee -a "$LOG_FILE"

echo "📦 Updating Python dependencies..." | tee -a "$LOG_FILE"
source "$REPO_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt | tee -a "$LOG_FILE"

echo "🔁 Restarting jesync_dashboard service..." | tee -a "$LOG_FILE"
sudo systemctl restart jesync_dashboard

echo "✅ Jesync Dashboard updated successfully." | tee -a "$LOG_FILE"
EOL

chmod +x updatejesync.sh
dos2unix updatejesync.sh

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

echo "🎉 Jesync Dashboard installed and running!"
echo "🌐 Access it at: http://<your-server-ip>:5000"
