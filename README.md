# ✅ Jesync Dashboard Installation Guide (Ubuntu 24.04)

This guide will walk you through installing the Jesync Dashboard — a Flask-based web GUI to view and edit Jesync & LibreQoS config files, with user login, role-based access, and dark mode support.

## 🔹 Prerequisites
Ensure you're using Ubuntu 24.04 and have:
- sudo access
- Internet connection
- Basic familiarity with Linux shell

## 🧱 1. Install Required Packages
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git nginx -y
```

## 📁 2. Set Up Project Directory
```bash
sudo mkdir -p /opt/libreqos/src
cd /opt/libreqos/src
sudo git clone https://your-git-repo-url/jesync_dashboard.git
cd jesync_dashboard
```
Replace the URL above with your real repo if you use Git.

## 🐍 3. Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you don’t have requirements.txt, you can create it with:
```txt
Flask
Flask-Login
Flask-SQLAlchemy
```

Then install:
```bash
pip install -r requirements.txt
```

## 🔑 4. Set Up User Permissions (for editing protected files like /etc/lqos.conf)
### Option A (Simplest): Run as root
No setup needed (we’ll configure systemd below).

### Option B (Safer): Use group access
```bash
sudo groupadd jesyncedit
sudo usermod -aG jesyncedit $USER
sudo chown root:jesyncedit /etc/lqos.conf
sudo chmod 664 /etc/lqos.conf
```
Then logout and log back in for group permissions to apply.

## ⚙️ 5. Create systemd Service (Run on Boot)
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
Environment="PATH=/opt/libreqos/src/jesync_dashboard/venv/bin"
ExecStart=/opt/libreqos/src/jesync_dashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## ▶️ 6. Enable and Start the Dashboard
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jesync_dashboard
sudo systemctl start jesync_dashboard
```

## 🌐 7. Access the Web Dashboard
Open your browser and go to:
```cpp
http://<your-server-ip>:5000
```

Example:
```cpp
http://10.254.254.254:5000
```

## 🔐 8. Login Credentials
Default users:
| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | adminpass | admin |
| viewer   | viewerpass| viewer|

You can manage users from the Manage Users button in the dashboard.

## 🎨 9. Features You Get
- Light/Dark Mode toggle 🌙
- User management with roles
- View/edit JSON, Python, and CONF files
- Excel-style CSV viewer with search
- Dashboard UI separated into:
  - 🔧 Jesync Integration Files
  - 📡 LibreQoS Files

## 🧪 10. Optional: Allow UFW/Firewall Access
```bash
sudo ufw allow 5000
```

## 🔁 Restart / Stop / Status
```bash
sudo systemctl restart jesync_dashboard
sudo systemctl stop jesync_dashboard
sudo systemctl status jesync_dashboard
```

## 🧼 Uninstall (optional)
```bash
sudo systemctl disable jesync_dashboard
sudo systemctl stop jesync_dashboard
sudo rm /etc/systemd/system/jesync_dashboard.service
sudo rm -rf /opt/libreqos/src/jesync_dashboard
```

## ✅ Done!
You now have a production-ready Jesync Dashboard that survives reboots, has permission to edit system files, and looks beautiful too 😎

Would you like me to:
- Turn this into a downloadable INSTALL.md or .pdf?
- Wrap it into a bash installer script?
- Make it deployable with Docker?

Just say the word!
