import json
import ast

FILES = {
    "jesync_static_device.json": "/opt/libreqos/src/jesync_static_device.json",
    "config.json": "/opt/libreqos/src/config.json",
    "updatecsv.py": "/opt/libreqos/src/updatecsv.py",
    "jesyncmt.json": "/opt/libreqos/src/jesync_dashboard/jesyncmt.json", 
    "network.json": "/opt/libreqos/src/network.json",
    "ShapedDevices.csv": "/opt/libreqos/src/ShapedDevices.csv",
    "lqos.conf": "/etc/lqos.conf",
    "memkill.py": "/opt/jesync_memkill/memkill.py",
    "updatecsv.service": "/etc/systemd/system/updatecsv.service",
    "50-cloud-init.yaml": "/etc/netplan/50-cloud-init.yaml",
    "libreqos.yaml": "/etc/netplan/libreqos.yaml"
}




VIEW_ONLY = ["ShapedDevices.csv"]  

def validate_and_save(filename, content):
    try:
        if filename.endswith(".json"):
            json.loads(content)
        elif filename.endswith(".py"):
            ast.parse(content)
        with open(FILES[filename], "w") as f:
            f.write(content)
        return True, "Saved successfully"
    except Exception as e:
        return False, str(e)
