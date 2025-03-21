from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from typing import Optional

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(120), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    vps_list = db.relationship('VPS', backref='user', lazy=True)

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

class VPS(db.Model):
    __tablename__ = 'vps'
    
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    ip_address: str = db.Column(db.String(45), nullable=False)
    node_exporter_port: int = db.Column(db.Integer, nullable=False)
    prometheus_port: int = db.Column(db.Integer, nullable=False)
    status: bool = db.Column(db.Boolean, default=False)
    last_checked: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grafana_dashboard_id: Optional[str] = db.Column(db.String(100), nullable=True)
    metrics = db.relationship('VPSMetrics', backref='vps', lazy=True)

    def __repr__(self):
        return f'<VPS {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'node_exporter_port': self.node_exporter_port,
            'prometheus_port': self.prometheus_port,
            'status': self.status,
            'last_checked': self.last_checked.isoformat(),
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'grafana_dashboard_id': self.grafana_dashboard_id,
            'metrics': [metric.to_dict() for metric in self.metrics] if self.metrics else None
        }

class VPSMetrics(db.Model):
    __tablename__ = 'vps_metrics'
    
    id: int = db.Column(db.Integer, primary_key=True)
    vps_id: int = db.Column(db.Integer, db.ForeignKey('vps.id'), nullable=False)
    cpu_usage: float = db.Column(db.Float, nullable=True)
    ram_usage: float = db.Column(db.Float, nullable=True)
    disk_usage: float = db.Column(db.Float, nullable=True)
    network_in: float = db.Column(db.Float, nullable=True)
    network_out: float = db.Column(db.Float, nullable=True)
    gpu_usage: Optional[float] = db.Column(db.Float, nullable=True)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<VPSMetrics for VPS {self.vps_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vps_id': self.vps_id,
            'cpu_usage': self.cpu_usage,
            'ram_usage': self.ram_usage,
            'disk_usage': self.disk_usage,
            'network_in': self.network_in,
            'network_out': self.network_out,
            'gpu_usage': self.gpu_usage,
            'updated_at': self.updated_at.isoformat()
        } 