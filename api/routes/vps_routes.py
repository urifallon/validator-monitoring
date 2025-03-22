from flask import request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import requests

from models import db, VPS
from api.routes import api_bp
from services.vps_service import check_vps_status

@api_bp.route('/vps', methods=['GET'])
@login_required
def get_all_vps():
    """Lấy danh sách VPS của người dùng hiện tại"""
    vps_list = VPS.query.filter_by(user_id=current_user.id).all()
    return jsonify([vps.to_dict() for vps in vps_list])

@api_bp.route('/vps/<int:vps_id>', methods=['GET'])
@login_required
def get_vps(vps_id):
    """Lấy thông tin chi tiết của một VPS"""
    vps = VPS.query.get_or_404(vps_id)
    
    # Kiểm tra quyền sở hữu
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Không có quyền truy cập VPS này'}), 403
    
    return jsonify(vps.to_dict())

@api_bp.route('/vps', methods=['POST'])
@login_required
def create_vps():
    """Tạo VPS mới"""
    data = request.json
    
    try:
        vps = VPS(
            name=data['name'],
            ip_address=data['ip_address'],
            port_exporter=data.get('port_exporter', 9100),
            port_promtail=data.get('port_promtail', 9080),
            user_id=current_user.id,
            status=False
        )
        
        db.session.add(vps)
        db.session.commit()
        
        return jsonify(vps.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/vps/<int:vps_id>', methods=['PUT'])
@login_required
def update_vps(vps_id):
    """Cập nhật thông tin VPS"""
    vps = VPS.query.get_or_404(vps_id)
    
    # Kiểm tra quyền sở hữu
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Không có quyền chỉnh sửa VPS này'}), 403
    
    data = request.json
    
    try:
        if 'name' in data:
            vps.name = data['name']
        if 'ip_address' in data:
            vps.ip_address = data['ip_address']
        if 'port_exporter' in data:
            vps.port_exporter = data['port_exporter']
        if 'port_promtail' in data:
            vps.port_promtail = data['port_promtail']
        
        db.session.commit()
        return jsonify(vps.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/vps/<int:vps_id>', methods=['DELETE'])
@login_required
def delete_vps(vps_id):
    """Xóa VPS"""
    vps = VPS.query.get_or_404(vps_id)
    
    # Kiểm tra quyền sở hữu
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Không có quyền xóa VPS này'}), 403
    
    try:
        db.session.delete(vps)
        db.session.commit()
        return jsonify({'message': 'VPS đã được xóa thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/vps/<int:vps_id>/status', methods=['GET'])
@login_required
def check_status(vps_id):
    """Kiểm tra trạng thái của VPS"""
    vps = VPS.query.get_or_404(vps_id)
    
    # Kiểm tra quyền sở hữu
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Không có quyền truy cập VPS này'}), 403
    
    status = check_vps_status(vps)
    
    # Cập nhật trạng thái trong database
    vps.status = status
    vps.last_checked = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'status': status}) 