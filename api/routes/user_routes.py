from flask import request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from api.routes import api_bp

@api_bp.route('/users/register', methods=['POST'])
def register():
    """Đăng ký người dùng mới"""
    data = request.json
    
    # Kiểm tra username và email đã tồn tại chưa
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Tên đăng nhập đã tồn tại'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email đã tồn tại'}), 400
    
    try:
        # Tạo user mới
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Đăng ký thành công',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/users/login', methods=['POST'])
def login():
    """Đăng nhập"""
    data = request.json
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401
    
    login_user(user)
    
    return jsonify({
        'message': 'Đăng nhập thành công',
        'user': user.to_dict()
    })

@api_bp.route('/users/logout', methods=['POST'])
@login_required
def logout():
    """Đăng xuất"""
    logout_user()
    return jsonify({'message': 'Đăng xuất thành công'})

@api_bp.route('/users/profile', methods=['GET'])
@login_required
def get_profile():
    """Lấy thông tin hồ sơ cá nhân"""
    return jsonify(current_user.to_dict())

@api_bp.route('/users/profile', methods=['PUT'])
@login_required
def update_profile():
    """Cập nhật hồ sơ cá nhân"""
    data = request.json
    
    try:
        if 'email' in data and data['email'] != current_user.email:
            # Kiểm tra email mới đã tồn tại chưa
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email đã tồn tại'}), 400
            current_user.email = data['email']
        
        if 'password' in data:
            current_user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cập nhật hồ sơ thành công',
            'user': current_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400 