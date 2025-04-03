#!/bin/bash

# ==========================================
# 🚀 JESYNC UI TOOL DASHBOARD Auto-Updater
# ==========================================

set -e

REPO_DIR="/opt/libreqos/src/jesync_dashboard"
BACKUP_DIR="/opt/jesyncbak/autoupdate_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$REPO_DIR/update.log"

echo "📦 Starting Jesync Dashboard update..." | tee -a "$LOG_FILE"
echo "🕒 $(date)" | tee -a "$LOG_FILE"

# Step 1: Backup
echo "📁 Backing up current dashboard to $BACKUP_DIR" | tee -a "$LOG_FILE"
mkdir -p "$BACKUP_DIR"
cp -r "$REPO_DIR"/* "$BACKUP_DIR"

# Step 2: Handle update conflict
cd "$REPO_DIR"
if [ -f "updatejesync.sh" ]; then
  echo "⚠️ Detected untracked updatejesync.sh — staging it to avoid conflict..." | tee -a "$LOG_FILE"
  git stash
fi

# Step 3: Pull latest
echo "⬇️ Pulling latest changes from GitHub..." | tee -a "$LOG_FILE"
git reset --hard
git pull origin main | tee -a "$LOG_FILE"

# Step 4: Reinstall Python deps
echo "📦 Installing Python dependencies..." | tee -a "$LOG_FILE"
source "$REPO_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt | tee -a "$LOG_FILE"

# Step 5: Restart service
echo "🔁 Restarting jesync_dashboard service..." | tee -a "$LOG_FILE"
sudo systemctl restart jesync_dashboard

echo "✅ Jesync Dashboard updated successfully." | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

# LICENSE & SUPPORT
cat <<EOF

## 📝 License
This project is licensed under the MIT License. See the LICENSE file for details.

---
### 💖 Support & Donations
If you find this project helpful, consider supporting its development.

Buy me a Coffee:
[PayPal](https://www.paypal.com/paypalme/jnhl)
EOF
