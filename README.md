# Jesync Dashboard – Full Installation Guide

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
