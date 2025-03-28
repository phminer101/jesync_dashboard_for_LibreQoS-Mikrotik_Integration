from flask_login import UserMixin
from db import UserModel

class User(UserMixin):
    def __init__(self, user_model):
        self.id = user_model.id
        self.username = user_model.username
        self.role = user_model.role

def get_user_by_username(username):
    return UserModel.query.filter_by(username=username).first()

def check_password(user, password):
    return user.password == password  # plaintext for now

def has_edit_access(user):
    return user.role == 'admin'
