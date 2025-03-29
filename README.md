# JESYNC UI TOOL DASHBOARD

**JESYNC UI TOOL DASHBOARD** is a powerful, user-friendly web interface designed to simplify the management and automation of Jesync configuration files, LibreQoS settings, system services, and backups. It brings modern usability to advanced system operations, particularly for environments using LibreQoS and MikroTik integrations.

---

A web-based GUI to manage Jesync and LibreQoS configuration files
![image](https://github.com/user-attachments/assets/8e5844bd-b8a4-45c1-8ffd-78a63d65ee51)
![image](https://github.com/user-attachments/assets/32b62b80-123b-40bc-9d8c-231d2532ef0a)
![image](https://github.com/user-attachments/assets/5232e647-9a58-4a9a-9503-19768f9205a0)
## 🚀 Key Features

### ✅ Intuitive Dashboard
- View and edit Jesync and LibreQoS configuration files from a centralized dashboard.
- Supports JSON, Python, CSV, and plain text files.
- View-only protection for sensitive or read-only roles.

### ✅ LibreQoS Integration
- Seamlessly manage essential LibreQoS files (`network.json`, `lqos.conf`, `ShapedDevices.csv`) directly from the UI.
- Restart LibreQoS services (`lqosd`, `lqos_node_manager`, `lqos_scheduler`) with a click.
- Auto-status display shows live health of services (active/inactive) using `systemctl`.

### ✅ Jesync Automation
- Designed for PisoWiFi-style systems that depend on Jesync + MikroTik API + updatecsv.py.
- Easily manage and restart `updatecsv.service` for automated device updates and control.

### ✅ User Management
- Role-based login system (admin and viewer).
- Admins can manage users, including creating, editing, or deleting accounts.
- Prevents accidental lockout (e.g., cannot delete last admin or self).

### ✅ File Backup & Restore
- One-click **Backup** and **Restore** options available for each editable file.
- Backups stored in `/opt/jesyncbak`, preserving historical changes.
- Ensures safe testing and editing with quick rollback capability.

### ✅ Systemd Service Integration
- JESYNC UI runs as a systemd service (`jesync_dashboard.service`).
- Hassle-free setup with one-line installation script.

---

## 💡 Why Use JESYNC UI TOOL?

Managing LibreQoS and Jesync manually can be tedious and error-prone — especially for less technical users. JESYNC UI TOOL streamlines the process:

- No need to SSH into your server to edit files.
- Avoid misconfigurations and typos with a clean editor.
- Visually confirm your service statuses without CLI commands.
- Quickly fix issues or roll back broken configs with backup & restore.

It’s an ideal companion for LibreQoS operators, PisoWifi developers, and system admins who value productivity, clarity, and peace of mind.

---

## ✅ Requirements

| Requirement       | Status                     |
|-------------------|----------------------------|
| OS                | Ubuntu 22.04 / 24.04       |
| Python            | Python 3.10+               |
| Privileges        | sudo or root               |
| Internet Access   | Required for installation  |

## 🚀 Quick Installation (One Command)

```bash
bash <(curl -sSL https://github.com/jesienazareth/jesync_dashboard/raw/main/install_jesync_dashboard.sh)

```

This will:
- Install dependencies
- Clone the repo from GitHub
- Set up virtual environment
- Create & enable systemd service
## 📦 Quick Installation

Clone and run the installer:

```bash
git clone https://github.com/jesienazareth/jesync_dashboard.git
cd jesync_dashboard
./install_jesync_dashboard.sh
```

---

## 🛠️ Usage

After installation, start the dashboard service:

```bash
sudo systemctl start jesync_dashboard.service
```

Enable the service to start on boot:

```bash
sudo systemctl enable jesync_dashboard.service
```

Access the dashboard in your browser at `http://<your_server_ip>:<port>`.

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
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

### 💖 Support & Donations

If you find this project helpful, consider supporting its development. Your donations are greatly appreciated and help to keep the project alive and growing.

**Buy me a Coffee:** [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-blue?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/jnhl)

Thank you for your support!
