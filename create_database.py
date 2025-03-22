from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_database():
    """
    Tạo dữ liệu mẫu cho ứng dụng
    """
    from models import db, User, VPS
    
    # Xóa dữ liệu cũ
    db.drop_all()
    db.create_all()
    
    # Tạo người dùng mẫu
    admin = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        email='admin@example.com'
    )
    
    test_user = User(
        username='testuser',
        password_hash=generate_password_hash('password123'),
        email='test@example.com'
    )
    
    db.session.add(admin)
    db.session.add(test_user)
    db.session.commit()
    
    # Tạo VPS mẫu cho admin
    vps1 = VPS(
        name='VPS Server 1',
        ip_address='192.168.1.100',
        port_exporter=9100,
        port_promtail=9080,
        status=True,
        user_id=admin.id,
        created_at=datetime.utcnow() - timedelta(days=10)
    )
    
    vps2 = VPS(
        name='VPS Server 2',
        ip_address='192.168.1.101',
        port_exporter=9100,
        port_promtail=9080,
        status=False,
        user_id=admin.id,
        created_at=datetime.utcnow() - timedelta(days=5)
    )
    
    # Tạo VPS mẫu cho test_user
    vps3 = VPS(
        name='Test Server',
        ip_address='192.168.1.200',
        port_exporter=9100,
        port_promtail=9080,
        status=True,
        user_id=test_user.id,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    
    db.session.add(vps1)
    db.session.add(vps2)
    db.session.add(vps3)
    db.session.commit()
    
    print("Dữ liệu mẫu đã được tạo thành công")
    
if __name__ == '__main__':
    from api import create_app
    from models import db
    
    app = create_app('development')
    with app.app_context():
        create_database() 