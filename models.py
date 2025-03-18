from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Tab(db.Model):
    __tablename__ = 'tab'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='OFF')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    metrics = db.relationship('TabMetrics', backref='tab', uselist=False)

    def __repr__(self):
        return f'<Tab {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'last_updated': self.last_updated.isoformat(),
            'metrics': self.metrics.to_dict() if self.metrics else None
        }

class TabMetrics(db.Model):
    __tablename__ = 'tab_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    tab_id = db.Column(db.Integer, db.ForeignKey('tab.id'), nullable=False)
    value1 = db.Column(db.Float, nullable=True)
    value2 = db.Column(db.Float, nullable=True)
    value3 = db.Column(db.Float, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TabMetrics for Tab {self.tab_id}>'

    def to_dict(self):
        return {
            'value1': self.value1,
            'value2': self.value2,
            'value3': self.value3,
            'updated_at': self.updated_at.isoformat()
        } 