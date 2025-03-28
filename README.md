# Jesync Dashboard – Full Installation Guide

A web-based GUI to manage Jesync and LibreQoS configuration files

## 📊 Features
- ✅ Edit .json, .py, .conf, and view .csv
- 🔒 Login system with role-based access
- 🌗 Built-in dark mode
- 🔁 Auto-start on boot via systemd

## ✅ Requirements

| Requirement       | Status                     |
|-------------------|----------------------------|
| OS                | Ubuntu 22.04 / 24.04       |
| Python            | Python 3.10+               |
| Privileges        | sudo or root               |
| Internet Access   | Required for installation  |

## 🚀 Quick Installation (One Command)

```bash
bash <(curl -sSL https://your-server/install_jesync_dashboard.sh)
```

This will:
- Install dependencies
- Clone the repo from GitHub
- Set up virtual environment
- Create & enable systemd service

## 🧱 Manual Installation (Step-by-Step)

### 🔹 Step 1: Update and Install Packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl nginx
```

### 🔹 Step 2: Clone the Dashboard

```bash
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .
```

### 🔹 Step 3: Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

If you have `requirements.txt`:

```bash
pip install -r requirements.txt
```

If not, install dependencies manually:

```bash
pip install Flask Flask-Login Flask-SQLAlchemy
```

### 🔹 Step 4: Allow Editing Protected Files (Optional)

If you want to edit system files like `/etc/lqos.conf` via the dashboard:

#### Option A – Run as Root ✅ Simple
No further steps needed.

#### Option B – Safer Group-Based Access

```bash
sudo groupadd jesyncedit
sudo usermod -aG jesyncedit $USER
sudo chown root:jesyncedit /etc/lqos.conf
sudo chmod 664 /etc/lqos.conf
```

🔁 Log out and back in for group access to take effect.

### 🔹 Step 5: Create systemd Service

```bash
sudo nano /etc/systemd/system/jesync_dashboard.service
```

Paste this:

```ini
[Unit]
Description=Jesync Dashboard Web UI
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/libreqos/src/jesync_dashboard
Environment=PATH=/opt/libreqos/src/jesync_dashboard/venv/bin
ExecStart=/opt/libreqos/src/jesync_dashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 🔹 Step 6: Enable and Start the Dashboard

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl start jesync_dashboard
```

### 🔹 Step 7: Access the Web Dashboard

Open your browser and visit:

```cpp
http://<your-server-ip>:5000
```

Example:

```cpp
http://192.168.1.100:5000
```

### 🔹 Step 8: Default Login Credentials

| Username | Password    | Role   |
|----------|-------------|--------|
| admin    | adminpass   | admin  |
| viewer   | viewerpass  | viewer |

You can manage users in the Manage Users section of the dashboard.

## 🔁 Useful Commands

| Action   | Command                                |
|----------|----------------------------------------|
| Start    | `sudo systemctl start jesync_dashboard`|
| Stop     | `sudo systemctl stop jesync_dashboard` |
| Restart  | `sudo systemctl restart jesync_dashboard`|
| Status   | `sudo systemctl status jesync_dashboard`|
| Logs     | `journalctl -u jesync_dashboard -e`    |

## 🌐 Optional: Allow Firewall Access

```bash
sudo ufw allow 5000
```

## 🧼 Uninstall (Optional)

```bash
sudo systemctl stop jesync_dashboard
sudo systemctl disable jesync_dashboard
sudo rm /etc/systemd/system/jesync_dashboard.service
sudo rm -rf /opt/libreqos/src/jesync_dashboard
```

## 🎨 Features Summary

- ✅ Edit .json, .py, .conf files
- ✅ Excel-style viewer for .csv
- ✅ Light/Dark Mode toggle
- ✅ Role-based access (Admin/Viewer)
- ✅ Web login system
- ✅ Auto-run on boot via systemd
- ✅ Root or group-based system file editing

- ## 💖 Support & Donations

If you find this project helpful, consider supporting its development. Your donations are greatly appreciated and help to keep the project alive and growing.

**Buy me a Coffee:** [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-blue?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/jnhl)

Thank you for your support!
