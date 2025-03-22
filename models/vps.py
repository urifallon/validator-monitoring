from datetime import datetime
from models import db

class VPS(db.Model):
    __tablename__ = 'vps'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    port_exporter = db.Column(db.Integer, nullable=False, default=9100)
    port_promtail = db.Column(db.Integer, nullable=False, default=9080)
    status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<VPS {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'port_exporter': self.port_exporter,
            'port_promtail': self.port_promtail,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'user_id': self.user_id
        } 