from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from create_database import create_database
from models import db, User, Tab, TabMetrics, VPS, VPSMetrics
import requests
import json
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GRAFANA_URL'] = 'http://your-grafana-url:3000'
app.config['GRAFANA_API_KEY'] = 'your-grafana-api-key'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/manage')
@login_required
def manage():
    return render_template('index.html')

@app.route('/stats')
@login_required
def stats():
    return render_template('index.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('index.html')

@app.route('/info')
@login_required
def info():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại')
            return redirect(url_for('signup'))
            
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công')
    return redirect(url_for('login'))

@app.route('/api/tabs')
@login_required
def get_tabs():
    tabs = Tab.query.all()
    return jsonify([{
        'id': tab.id,
        'name': tab.name,
        'status': tab.status
    } for tab in tabs])

@app.route('/api/tabs/<int:tab_id>/metrics')
@login_required
def get_tab_metrics(tab_id):
    metrics = TabMetrics.query.filter_by(tab_id=tab_id).first()
    if metrics:
        return jsonify({
            'value1': metrics.value1,
            'value2': metrics.value2,
            'value3': metrics.value3
        })
    return jsonify({'error': 'Không tìm thấy metrics'}), 404

@app.route('/api/vps', methods=['GET'])
@login_required
def get_vps_list():
    vps_list = VPS.query.filter_by(user_id=current_user.id).all()
    return jsonify([vps.to_dict() for vps in vps_list])

@app.route('/api/vps', methods=['POST'])
@login_required
def add_vps():
    data = request.json
    try:
        # Xác định port nào là port node_exporter và prometheus dựa trên loại
        if data['type'] == 'nodeexporter':
            node_exporter_port = data['port']
            prometheus_port = 9090  # Port mặc định cho Prometheus
        elif data['type'] == 'prometheus':
            node_exporter_port = 9100  # Port mặc định cho Node Exporter
            prometheus_port = data['port']
        else:  # custom
            node_exporter_port = data['port']
            prometheus_port = 9090  # Port mặc định cho Prometheus
            
        vps = VPS(
            name=data['name'],
            ip_address=data['ip_address'],
            node_exporter_port=node_exporter_port,
            prometheus_port=prometheus_port,
            user_id=current_user.id
        )
        db.session.add(vps)
        db.session.commit()
        
        # Create Grafana dashboard for this VPS
        dashboard_id = create_grafana_dashboard(vps)
        if dashboard_id:
            vps.grafana_dashboard_id = dashboard_id
            db.session.commit()
        
        return jsonify(vps.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': str(e)}), 400

@app.route('/api/vps/<int:vps_id>', methods=['DELETE'])
@login_required
def delete_vps(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete Grafana dashboard
    if vps.grafana_dashboard_id:
        delete_grafana_dashboard(vps.grafana_dashboard_id)
    
    db.session.delete(vps)
    db.session.commit()
    return jsonify({'message': 'VPS deleted successfully'})

@app.route('/api/vps/<int:vps_id>/status', methods=['GET'])
@login_required
def check_vps_status(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ping the VPS to check status
    try:
        response = requests.get(f"http://{vps.ip_address}:{vps.node_exporter_port}/metrics", timeout=5)
        status = response.status_code == 200
    except:
        status = False
    
    vps.status = status
    vps.last_checked = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'status': status})

@app.route('/api/vps/<int:vps_id>/metrics', methods=['GET'])
@login_required
def get_vps_metrics(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    if vps.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get metrics from Prometheus
    try:
        metrics = get_prometheus_metrics(vps)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_grafana_dashboard(vps):
    # Tạm thời trả về dashboard_id giả lập
    # Trong thực tế, bạn sẽ gọi API của Grafana để tạo dashboard
    try:
        # Trong thực tế, bạn sẽ tạo dashboard trong Grafana và lấy ID
        # Ví dụ:
        # headers = {'Authorization': f'Bearer {app.config["GRAFANA_API_KEY"]}'}
        # payload = {...}  # Cấu trúc dashboard tương ứng với Grafana API
        # response = requests.post(f'{app.config["GRAFANA_URL"]}/api/dashboards/db', 
        #                         headers=headers, json=payload)
        # return response.json()['id']
        
        # Trả về một ID giả lập để demo
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"dashboard-{random_id}"
    except Exception as e:
        print(f"Error creating Grafana dashboard: {e}")
        return None

def delete_grafana_dashboard(dashboard_id):
    # Trong thực tế, bạn sẽ gọi API của Grafana để xóa dashboard
    # Ví dụ:
    # headers = {'Authorization': f'Bearer {app.config["GRAFANA_API_KEY"]}'}
    # response = requests.delete(f'{app.config["GRAFANA_URL"]}/api/dashboards/uid/{dashboard_id}', 
    #                           headers=headers)
    # return response.status_code == 200
    return True

def get_prometheus_metrics(vps):
    # Giả lập dữ liệu metrics
    return {
        'cpu_usage': round(random.uniform(0, 100), 2),
        'ram_usage': round(random.uniform(0, 100), 2),
        'disk_usage': round(random.uniform(0, 100), 2),
        'network_in': round(random.uniform(0, 1000), 2),
        'network_out': round(random.uniform(0, 1000), 2),
        'gpu_usage': round(random.uniform(0, 100), 2) if random.random() > 0.5 else None
    }

if __name__ == '__main__':
    with app.app_context():
        # Tạo database và các bảng
        db.create_all()
        # Tạo dữ liệu mẫu
        create_database()
    app.run(debug=True) 