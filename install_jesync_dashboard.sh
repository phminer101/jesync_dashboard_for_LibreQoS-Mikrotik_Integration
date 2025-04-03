#!/bin/bash
# =========================================
# 📦 JESYNC UI TOOL DASHBOARD INSTALLER
# =========================================

set -e

echo "🔧 Updating packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl nginx dos2unix

echo "📁 Cloning Dashboard..."
sudo mkdir -p /opt/jesync_dashboard
cd /opt/jesync_dashboard

if [ ! -d .git ]; then
  sudo git clone https://github.com/jesienazareth/jesync_dashboard.git .
fi

sudo chown -R "$USER:$USER" .

# ✅ Create backup directory with proper permissions
sudo mkdir -p /opt/jesyncbak
sudo chmod 755 /opt/jesyncbak

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
REPO_DIR="/opt/jesync_dashboard"
BACKUP_DIR="/opt/jesync_dashboard/backups/autoupdate_$(date +%Y%m%d_%H%M%S)"
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

echo "🛠️ Installing jesync_dashboard systemd service..."

sudo tee /etc/systemd/system/jesync_dashboard.service > /dev/null <<EOF
[Unit]
Description=Jesync Dashboard Service
After=network.target

[Service]
WorkingDirectory=/opt/jesync_dashboard
ExecStart=/opt/jesync_dashboard/venv/bin/python /opt/jesync_dashboard/app.py
Restart=always
User=www-data
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd and starting Jesync Dashboard..."
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl restart jesync_dashboard

echo "✅ Jesync Dashboard installation complete and running at: http://<your-server-ip>:5000"
