"""Data models."""
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'flaskloginUsers'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(100),
        nullable=False,
        unique=False
    )
    email = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(200),
        primary_key=False,
        unique=False,
        nullable=False
	)
    name = db.Column(
        db.String(60),
        index=False,
        unique=False,
        nullable=True
	)
    created = db.Column(
        db.String(60),
        index=False,
        unique=False,
        nullable=True
    )
    lastLogin = db.Column(
        db.String(60),
        index=False,
        unique=False,
        nullable=True
    )
    isAdmin = db.Column(
        db.String(60),
        unique=False
    )
    database = db.Column(
        db.Integer,
        unique=False
    )
    isActive = db.Column(
        db.String(60),
        unique=False
    )
    language = db.Column(
        db.String(60),
        unique=False
    )

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
