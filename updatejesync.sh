#!/bin/bash

# ==========================================
# 🚀 JESYNC UI TOOL DASHBOARD Auto-Updater
# ==========================================

set -e  # Exit immediately on error

REPO_DIR="/opt/libreqos/src/jesync_dashboard"
BACKUP_DIR="/opt/jesyncbak/autoupdate_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$REPO_DIR/update.log"

echo "📦 Starting Jesync Dashboard update..." | tee -a "$LOG_FILE"
echo "🕒 $(date)" | tee -a "$LOG_FILE"
 
# Step 1: Backup current files
echo "📁 Backing up current dashboard to $BACKUP_DIR" | tee -a "$LOG_FILE"
mkdir -p "$BACKUP_DIR"
cp -r "$REPO_DIR"/* "$BACKUP_DIR"

# Step 2: Pull latest updates from GitHub
echo "⬇️ Pulling latest changes from GitHub..." | tee -a "$LOG_FILE"
cd "$REPO_DIR"

# Handle untracked updatejesync.sh safely
if [ -f "$REPO_DIR/updatejesync.sh" ] && ! git ls-files --error-unmatch updatejesync.sh > /dev/null 2>&1; then
  echo "⚠️ Detected untracked updatejesync.sh — staging it to avoid conflict..." | tee -a "$LOG_FILE"
  git add updatejesync.sh
fi

git stash save "Local changes before auto-update" || true
git pull origin main | tee -a "$LOG_FILE"
git stash pop || true


# Step 3: Reinstall/update Python dependencies
echo "📦 Installing Python dependencies..." | tee -a "$LOG_FILE"
source "$REPO_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt | tee -a "$LOG_FILE"

# Step 4: Restart systemd service
echo "🔁 Restarting jesync_dashboard service..." | tee -a "$LOG_FILE"
sudo systemctl restart jesync_dashboard

echo "✅ Jesync Dashboard updated successfully." | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

################################################################################
## 📝 License
##
## This project is licensed under the MIT License.
## See the LICENSE file for details.
##
## ----------------------------------------------------------------------------
## 💖 Support & Donations
##
## If you find this project helpful, consider supporting its development.
## Your donations are greatly appreciated and help to keep the project alive.
##
## Buy me a Coffee:
## [Donate via PayPal](https://www.paypal.com/paypalme/jnhl)
## [Subscribe ]("https://facebook.com/jesync28)
## Thank you for your support!
################################################################################
