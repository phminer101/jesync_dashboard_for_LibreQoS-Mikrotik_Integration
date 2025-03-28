from flask import Flask
from db import db, UserModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    if not UserModel.query.filter_by(username="admin").first():
        db.session.add(UserModel(username="admin", password="adminpass", role="admin"))
        print("✅ Created admin user.")

    if not UserModel.query.filter_by(username="viewer").first():
        db.session.add(UserModel(username="viewer", password="viewerpass", role="viewer"))
        print("✅ Created viewer user.")

    db.session.commit()
    print("🎉 Done seeding users.")
