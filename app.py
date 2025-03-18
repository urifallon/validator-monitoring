from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from create_database import create_database
from models import db, User, Tab, TabMetrics

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    tabs = Tab.query.all()
    return render_template('index.html', tabs=tabs)

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

if __name__ == '__main__':
    with app.app_context():
        # Tạo database và các bảng
        db.create_all()
        # Tạo dữ liệu mẫu
        create_database()
    app.run(debug=True) 