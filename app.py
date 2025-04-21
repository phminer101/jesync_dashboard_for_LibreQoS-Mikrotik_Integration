from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from db import db, UserModel
from auth import User, get_user_by_username, check_password, has_edit_access
from config import FILES, validate_and_save
from routeros_api import RouterOsApiPool
import subprocess
import os
import shutil
import json
import secrets
import psutil
import socket
import csv
from flask import request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

BACKUP_DIR = "/opt/jesyncbak"
os.makedirs(BACKUP_DIR, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    user_model = UserModel.query.get(int(user_id))
    return User(user_model) if user_model else None

def get_service_status(service):
    try:
        result = subprocess.run(
            ["/bin/systemctl", "is-active", service],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "inactive"

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_user_by_username(request.form["username"])
        if user and check_password(user, request.form["password"]):
            login_user(User(user))
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    service_list = ["lqosd", "lqos_node_manager", "lqos_scheduler", "updatecsv", "jesync_dashboard.service"]
    service_statuses = {s: get_service_status(s) for s in service_list}


    return render_template("dashboard.html", files=FILES.keys(), user=current_user,
                           service_statuses=service_statuses,
                           mikrotik_data=[], total_hotspot=0, total_pppoe=0)

@app.route("/api/active_sessions")
@login_required
def api_active_sessions():
    mikrotik_routers = load_mikrotik_config()
    mikrotik_data = []
    total_hotspot = 0
    total_pppoe = 0

    for router in mikrotik_routers:
        hotspot_count, pppoe_count = fetch_active_sessions(router)
        mikrotik_data.append({
            "name": router["name"],
            "address": router["address"],
            "hotspot": hotspot_count,
            "pppoe": pppoe_count
        })
        total_hotspot += hotspot_count
        total_pppoe += pppoe_count

    return jsonify({
        "mikrotik_data": mikrotik_data,
        "total_hotspot": total_hotspot,
        "total_pppoe": total_pppoe
    })

def load_mikrotik_config():
    CONFIG_PATH = "/opt/libreqos/src/jesync_dashboard/jesyncmt.json"
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("routers", [])
    except Exception as e:
        print(f"Failed to load MikroTik config: {e}")
        return []

def fetch_active_sessions(router):
    active_hotspot = 0
    active_pppoe = 0
    try:
        api_pool = RouterOsApiPool(
            host=router["address"],
            username=router["username"],
            password=router["password"],
            port=router.get("port", 8728),
            use_ssl=False,
            plaintext_login=True
        )
        api = api_pool.get_api()

        if router.get("hotspot", True):
            hotspot_resource = api.get_resource("/ip/hotspot/active")
            active_hotspot = len(hotspot_resource.get())

        if router.get("pppoe", True):
            pppoe_resource = api.get_resource("/ppp/active")
            all_sessions = pppoe_resource.get()


            filtered_sessions = [
                s for s in all_sessions
                if "comment" not in s or "dis" not in s["comment"].lower()
            ]

            active_pppoe = len(filtered_sessions)

    except Exception as e:
        print(f"[{router.get('name')}] API Error: {e}")
    return active_hotspot, active_pppoe

@app.route("/edit/<filename>")
@login_required
def edit_file(filename):
    if filename not in FILES:
        return "Invalid file", 404
    with open(FILES[filename], "r") as f:
        content = f.read()

    if filename.endswith(".json"):
        file_type = "json"
    elif filename.endswith(".py") or filename.endswith(".conf"):
        file_type = "python"
    elif filename.endswith(".csv"):
        file_type = "csv"
    else:
        file_type = "text"

    view_only = filename.endswith(".csv") or not has_edit_access(current_user)
    return render_template("editor.html", filename=filename, content=content,
                       file_type=file_type, can_edit=not view_only)


@app.route("/api/save/<filename>", methods=["POST"])
@login_required
def save_file(filename):
    if not has_edit_access(current_user):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    if filename not in FILES or filename.endswith(".csv"):
        return jsonify({"status": "error", "message": "Read-only or invalid file"}), 400

    content = request.json.get("content", "")
    success, message = validate_and_save(filename, content)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": message}), 400

@app.route("/backup/<filename>", methods=["POST"])
@login_required
def backup_file(filename):
    if filename not in FILES:
        flash("Invalid file.")
        return redirect(url_for("dashboard"))
    src = FILES[filename]
    dst = os.path.join(BACKUP_DIR, filename + ".bak")
    try:
        shutil.copy(src, dst)
        flash(f"{filename} backed up.")
    except Exception as e:
        flash(f"Backup failed: {str(e)}")
    return redirect(url_for("dashboard"))

@app.route("/restore/<filename>", methods=["POST"])
@login_required
def restore_file(filename):
    if filename not in FILES:
        flash("Invalid file.")
        return redirect(url_for("dashboard"))
    src = os.path.join(BACKUP_DIR, filename + ".bak")
    dst = FILES[filename]
    try:
        if not os.path.exists(src):
            flash(f"No backup found for {filename}")
            return redirect(url_for("dashboard"))
        shutil.copy(src, dst)
        flash(f"{filename} restored from backup.")
    except Exception as e:
        flash(f"Restore failed: {str(e)}")
    return redirect(url_for("dashboard"))

@app.route("/users")
@login_required
def users():
    if current_user.role != "admin":
        return "Access denied", 403
    user_list = UserModel.query.all()
    return render_template("users.html", users=user_list)

@app.route("/users/add", methods=["GET", "POST"])
@login_required
def add_user():
    if current_user.role != "admin":
        return "Access denied", 403
    if request.method == "POST":
        try:
            new_user = UserModel(
                username=request.form["username"],
                password=request.form["password"],
                role=request.form["role"]
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User added.")
            return redirect(url_for("users"))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists.")
    return render_template("user_form.html", mode="add")

@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if current_user.role != "admin":
        return "Access denied", 403
    user = UserModel.query.get_or_404(user_id)
    if request.method == "POST":
        if user.username == "admin" and request.form["role"] != "admin":
            flash("Cannot demote main admin.")
            return redirect(url_for("users"))
        user.password = request.form["password"]
        user.role = request.form["role"]
        db.session.commit()
        flash("User updated.")
        return redirect(url_for("users"))
    return render_template("user_form.html", mode="edit", user=user)

@app.route("/users/delete/<int:user_id>")
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        return "Access denied", 403
    user = UserModel.query.get_or_404(user_id)
    if user.username == current_user.username:
        flash("You cannot delete yourself.")
        return redirect(url_for("users"))
    if user.role == "admin" and UserModel.query.filter_by(role="admin").count() <= 1:
        flash("At least one admin must remain.")
        return redirect(url_for("users"))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect(url_for("users"))

@app.route("/restart/<service>", methods=["POST"])
@login_required
def restart_specific_service(service):
    allowed = ["lqosd", "lqos_node_manager", "lqos_scheduler", "updatecsv"]
    if service not in allowed:
        flash(f"{service} is not an allowed service.")
        return redirect(url_for("dashboard"))
    try:
        subprocess.run(["/bin/systemctl", "restart", service], check=True)
        flash(f"{service} restarted successfully.")
    except subprocess.CalledProcessError:
        flash(f"Failed to restart {service}.")
    return redirect(url_for("dashboard"))

@app.route("/update_jesync", methods=["POST"])
@login_required
def update_jesync():
    script_path = "/opt/libreqos/src/jesync_dashboard/updatejesync.sh"
    try:
        subprocess.run(["/bin/bash", script_path], check=True)
        flash("Jesync updated successfully.")
    except subprocess.CalledProcessError as e:
        flash(f"Update failed: {e}")
    return redirect(url_for("dashboard"))

@app.route("/api/local_interfaces")
@login_required
def local_interfaces():
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    result = {}
    for name, info in interfaces.items():
        if name == "lo":
            continue  # skip loopback

        ip = next((i.address for i in info if i.family == socket.AF_INET), None)
        status = stats[name].isup if name in stats else False

        result[name] = {
            "status": status,
            "ip": ip or "N/A"
        }

    return jsonify(result)

from flask import flash, redirect, url_for
import os

@app.route('/wipe_file/<filename>', methods=['POST'])
def wipe_file(filename):
    try:
        if filename == 'ShapedDevices.csv':
            file_path = '/opt/libreqos/src/ShapedDevices.csv'

            with open(file_path, 'r') as f:
                rows = list(csv.reader(f))

            # Preserve only header + first data row
            preserved = rows[:2]  # row[0] = header, row[1] = first row (usually test/dummy)

            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(preserved)

            flash('✅ ShapedDevices.csv wiped (except for first row)', 'success')
        else:
            # fallback for other file types
            file_path = os.path.join('/opt/libreqos/src/jesync_dashboard', filename)
            open(file_path, 'w').close()
            flash(f'✅ {filename} wiped.', 'success')

    except Exception as e:
        flash(f"❌ Error wiping file: {str(e)}", 'danger')

    return redirect(url_for('edit_file', filename=filename))




@app.route('/add_shaped_device', methods=['POST'])
def add_shaped_device():
    try:
        print("🟢 Add Entry Triggered")

        new_row = {
            'Circuit ID': request.form.get('circuit_id', ''),
            'Circuit Name': request.form.get('circuit_name', ''),
            'Device ID': request.form.get('device_id', ''),
            'Device Name': request.form.get('device_name', ''),
            'Parent Node': request.form.get('parent_node', ''),
            'MAC': request.form.get('mac', ''),
            'IPv4': request.form.get('ipv4', ''),
            'IPv6': request.form.get('ipv6', ''),
            'Download Min Mbps': request.form.get('download_min', ''),
            'Upload Min Mbps': request.form.get('upload_min', ''),
            'Download Max Mbps': request.form.get('download_max', ''),
            'Upload Max Mbps': request.form.get('upload_max', ''),
            'Comment': request.form.get('comment', '')
        }

        csv_path = "/opt/libreqos/src/ShapedDevices.csv"

        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=new_row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_row)

        flash("✅ Entry added successfully!", "success")
    except Exception as e:
        flash(f"❌ Error adding entry: {str(e)}", "danger")

    return redirect(url_for('edit_file', filename='ShapedDevices.csv'))

@app.route('/delete_shaped_device/<int:index>', methods=['POST'])
def delete_shaped_device(index):
    try:
        csv_path = "/opt/libreqos/src/ShapedDevices.csv"

        with open(csv_path, 'r') as f:
            rows = list(csv.reader(f))

        header = rows[0]
        data = rows[1:]

        if 0 <= index < len(data):
            del data[index]

            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(data)

            flash("✅ Entry deleted successfully!", "success")
        else:
            flash("❌ Invalid row index!", "danger")

    except Exception as e:
        flash(f"❌ Error deleting entry: {str(e)}", "danger")

    return redirect(url_for('edit_file', filename='ShapedDevices.csv'))

@app.route("/upload_csv/<filename>", methods=["POST"])
@login_required
def upload_csv(filename):
    if not has_edit_access(current_user):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    if filename != "ShapedDevices.csv":
        flash("Only ShapedDevices.csv is allowed for upload.", "danger")
        return redirect(url_for("dashboard"))

    if "csv_file" not in request.files:
        flash("No file uploaded.", "warning")
        return redirect(url_for("edit_file", filename=filename))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("Empty file name.", "warning")
        return redirect(url_for("edit_file", filename=filename))

    try:
        file.save(FILES[filename])
        flash("ShapedDevices.csv uploaded and replaced successfully.", "success")
    except Exception as e:
        flash(f"Upload failed: {e}", "danger")

    return redirect(url_for("edit_file", filename=filename))

@app.context_processor
def inject_version():
    try:
        with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
            return {"version": f.read().strip()}
    except:
        return {"version": "Unknown"}

@app.route("/api/version")
def get_version():
    try:
        with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
            return jsonify({"version": f.read().strip()})
    except:
        return jsonify({"version": "Unknown"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not UserModel.query.filter_by(username="admin").first():
            db.session.add(UserModel(username="admin", password="adminpass", role="admin"))
        if not UserModel.query.filter_by(username="viewer").first():
            db.session.add(UserModel(username="viewer", password="viewerpass", role="viewer"))
        db.session.commit()
    app.run(host="0.0.0.0", port=5000, debug=True)
