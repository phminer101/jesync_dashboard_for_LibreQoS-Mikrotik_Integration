# 📊 Jesync Dashboard Installation Guide

> A web-based GUI to manage Jesync and LibreQoS configuration files.

---

## ✅ Requirements

- Ubuntu 22.04 / 24.04
- Python 3.10+
- Internet connection
- Access to `/etc/lqos.conf` (optional)
- Root or sudo privileges

---

## 🚀 Quick Install (One Command)

> For clean systems or automation:

```bash
bash <(curl -sSL https://your-server/install_jesync_dashboard.sh)
```

## 🧱 Manual Installation (Step-by-Step)

### 1. System Update & Tools

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip git nginx curl -y
```

### 2. Clone the Dashboard

```bash
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
sudo chown -R $USER:$USER .
```

### 3. Setup Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If no requirements.txt, run:

```bash
pip install Flask Flask-Login Flask-SQLAlchemy
```

### 4. Optional: Enable Editing Protected Files (e.g., /etc/lqos.conf)

#### Option A: Run as root ✅ Simple

No permission changes needed.

#### Option B: Safer group-based access

```bash
sudo groupadd jesyncedit
sudo usermod -aG jesyncedit $USER
sudo chown root:jesyncedit /etc/lqos.conf
sudo chmod 664 /etc/lqos.conf
```

Then logout and login again to apply group changes.

### 5. Create systemd Service

```bash
sudo nano /etc/systemd/system/jesync_dashboard.service
```

Paste:

```ini
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
```

### 6. Enable & Start the Service

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl start jesync_dashboard
```

### 7. Access the GUI

Open your browser:

```cpp
http://<your-server-ip>:5000
```

### 8. Default Users

| Username | Password   | Role   |
|----------|------------|--------|
| admin    | adminpass  | admin  |
| viewer   | viewerpass | viewer |

---

## 🔁 Commands

| Action  | Command                               |
|---------|---------------------------------------|
| Start   | `sudo systemctl start jesync_dashboard` |
| Stop    | `sudo systemctl stop jesync_dashboard`  |
| Restart | `sudo systemctl restart jesync_dashboard` |
| View Logs | `journalctl -u jesync_dashboard -e`    |

---

## 🧼 Uninstall

```bash
sudo systemctl stop jesync_dashboard
sudo systemctl disable jesync_dashboard
sudo rm /etc/systemd/system/jesync_dashboard.service
sudo rm -rf /opt/libreqos/src/jesync_dashboard
```

---

## ✅ Features

- File manager for .json, .py, .conf
- View .csv with Excel-style search
- Role-based login (admin/viewer)
- Live dark mode toggle
- Systemd integration (runs on boot)
- Safe root-level editing (optional)
