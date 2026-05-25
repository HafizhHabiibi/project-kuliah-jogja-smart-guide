from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    preferences = db.Column(db.Text, default='[]')  # JSON string of preferred categories
    pref_nature = db.Column(db.Integer, default=3, nullable=False)
    pref_culture = db.Column(db.Integer, default=3, nullable=False)
    pref_culinary = db.Column(db.Integer, default=3, nullable=False)
    pref_crowd = db.Column(db.Integer, default=3, nullable=False)
    pref_effort = db.Column(db.Integer, default=3, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
