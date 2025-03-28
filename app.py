from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from db import db, UserModel
from auth import User, get_user_by_username, check_password, has_edit_access
from config import FILES, validate_and_save

app = Flask(__name__)
app.secret_key = "your-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user_model = UserModel.query.get(int(user_id))
    return User(user_model) if user_model else None

# =======================
# ROUTES
# =======================

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
    return render_template("dashboard.html", files=FILES.keys(), user=current_user)

@app.route("/edit/<filename>")
@login_required
def edit_file(filename):
    if filename not in FILES:
        return "Invalid file", 404

    with open(FILES[filename], "r") as f:
        content = f.read()

    # File type detection
    if filename.endswith(".json"):
        file_type = "json"
    elif filename.endswith(".py") or filename.endswith(".conf"):
        file_type = "python"
    elif filename.endswith(".csv"):
        file_type = "csv"
    else:
        file_type = "text"

    # View-only logic
    view_only = filename.endswith(".csv") or not has_edit_access(current_user)

    return render_template(
        "editor.html",
        filename=filename,
        content=content,
        file_type=file_type,
        can_edit=not view_only
    )

@app.route("/api/save/<filename>", methods=["POST"])
@login_required
def save_file(filename):
    if not has_edit_access(current_user):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    if filename not in FILES or filename.endswith(".csv"):
        return jsonify({"status": "error", "message": "Read-only file or invalid file"}), 400

    content = request.json.get("content", "")
    success, message = validate_and_save(filename, content)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": message}), 400

# =======================
# USER MANAGEMENT (ADMIN)
# =======================

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
            flash("User added successfully.")
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
            flash("Cannot change role of main admin.")
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
    admin_count = UserModel.query.filter_by(role="admin").count()
    if user.role == "admin" and admin_count <= 1:
        flash("At least one admin is required.")
        return redirect(url_for("users"))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect(url_for("users"))

# =======================
# MAIN ENTRY
# =======================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not UserModel.query.filter_by(username="admin").first():
            db.session.add(UserModel(username="admin", password="adminpass", role="admin"))
        if not UserModel.query.filter_by(username="viewer").first():
            db.session.add(UserModel(username="viewer", password="viewerpass", role="viewer"))
        db.session.commit()

    app.run(host="0.0.0.0", port=5000, debug=True)
