# Jesync Dashboard – Full Installation Guide (Ubuntu 24.04)

A web-based GUI to manage Jesync and LibreQoS configuration files

- ✅ Edit .json, .py, .conf, and view .csv
- 🔒 Login system with role-based access
- 🌗 Built-in dark mode
- 🔁 Auto-start on boot via systemd

## ✅ Requirements

| Requirement       | Description                  |
|-------------------|------------------------------|
| **OS**            | Ubuntu 22.04 / 24.04         |
| **Python**        | Python 3.10+                 |
| **Privileges**    | sudo or root                 |
| **Internet Access**| Required for install         |

## 🚀 Option 1: Quick One-Line Installer (Recommended)

Automatically installs everything via script

```bash
bash <(curl -sSL https://github.com/jesienazareth/jesync_dashboard/raw/main/install_jesync_dashboard.sh)
```
### Or
## To Use:

### Locate the file:

```bash
install_jesync_dashboard.sh
```

### Then run:

```bash
chmod +x install_jesync_dashboard.sh
./install_jesync_dashboard.sh
```

### Or remotely (if hosted online):

```bash
bash <(curl -sSL https://yourhost.com/install_jesync_dashboard.sh)
```

### What it does:
- Installs system dependencies
- Clones the latest dashboard from GitHub
- Sets up Python venv
- Installs Flask & dependencies
- Creates a systemd service (runs as root)
- Starts the dashboard

## 🧱 Option 2: Manual Installation (Step-by-Step)

### 🔹 1. Update System & Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl nginx
```

### 🔹 2. Clone the Dashboard
```bash
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .
```

### 🔹 3. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

#### If requirements.txt is missing:
```bash
pip install Flask Flask-Login Flask-SQLAlchemy
```

### 🔹 4. (Optional) Enable Editing Protected Files
Only if you need to edit files like /etc/lqos.conf through the GUI

#### Option A – Run Dashboard as root ✅ Easy (default in installer)
No changes required.

#### Option B – Use Safer Group-Based Permissions
```bash
sudo groupadd jesyncedit
sudo usermod -aG jesyncedit $USER
sudo chown root:jesyncedit /etc/lqos.conf
sudo chmod 664 /etc/lqos.conf
```

🔄 Log out and log back in for group changes to apply.

### 🔹 5. Create systemd Service
```bash
sudo nano /etc/systemd/system/jesync_dashboard.service
```

#### Paste this:
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

### 🔹 6. Enable & Start the Dashboard
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl start jesync_dashboard
```

### 🔹 7. Access the Web Interface
In your browser:
```cpp
http://<your-server-ip>:5000
```

Example:
```cpp
http://192.168.1.100:5000
```

### 🔐 8. Default Login

| Username | Password   | Role   |
|----------|------------|--------|
| admin    | adminpass  | admin  |
| viewer   | viewerpass | viewer |

✅ Manage users via Manage Users in the dashboard UI.

## 🔁 Management Commands

| Action  | Command                           |
|---------|-----------------------------------|
| Start   | `sudo systemctl start jesync_dashboard`   |
| Stop    | `sudo systemctl stop jesync_dashboard`    |
| Restart | `sudo systemctl restart jesync_dashboard` |
| Status  | `sudo systemctl status jesync_dashboard`  |
| Logs    | `journalctl -u jesync_dashboard -e`       |

## 🌐 (Optional) Allow Firewall Port 5000
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

## 🎨 Features

- ✅ Role-based login system
- ✅ Dark mode toggle
- ✅ File manager for .json, .py, .conf
- ✅ Excel-style .csv viewer
- ✅ User management from the web UI
- ✅ systemd auto-start on boot
- ✅ Optional secure root file editing
