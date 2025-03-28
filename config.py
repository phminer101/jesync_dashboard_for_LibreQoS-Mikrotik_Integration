import json
import ast

FILES = {
    # Jesync Integration
    "jesync_static_device.json": "/opt/libreqos/src/jesync_static_device.json",
    "config.json": "/opt/libreqos/src/config.json",
    "jesynclqos.py": "/opt/libreqos/src/jesynclqos.py",

    # LibreQos
    "network.json": "/opt/libreqos/src/network.json",
    "ShapedDevices.csv": "/opt/libreqos/src/ShapedDevices.csv",
    "lqos.conf": "/etc/lqos.conf"
}

VIEW_ONLY = ["ShapedDevices.csv"]  # mark which files are read-only

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
