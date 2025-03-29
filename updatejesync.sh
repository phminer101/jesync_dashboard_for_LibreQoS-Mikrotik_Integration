#!/bin/bash

# Auto Update Script for Jesync UI Tool Dashboard
# GitHub: https://github.com/jesienazareth/jesync_dashboard

set -e

APP_DIR="/opt/libreqos/src/jesync_dashboard"
VENV_PATH="$APP_DIR/venv/bin/activate"
SERVICE_NAME="jesync_dashboard"

echo "🔄 Updating Jesync UI Tool Dashboard..."

# 1. Navigate to the app directory
cd "$APP_DIR" || { echo "❌ App directory not found: $APP_DIR"; exit 1; }

# 2. Optional: Stash local changes to prevent merge issues
echo "📦 Stashing local changes (if any)..."
git stash --include-untracked || true

# 3. Pull the latest changes from GitHub
echo "⬇️ Pulling latest changes from GitHub..."
git pull origin main

# 4. Activate the virtual environment
echo "🐍 Activating Python virtual environment..."
source "$VENV_PATH"

# 5. Install/upgrade Python dependencies
echo "📦 Installing/updating Python requirements..."
pip install -r requirements.txt

# 6. Restart the dashboard service
echo "🚀 Restarting $SERVICE_NAME service..."
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Jesync Dashboard successfully updated and restarted!"


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
