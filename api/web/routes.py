from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, VPS
from api.web import web_bp

@web_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@web_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@web_bp.route('/manage')
@login_required
def manage():
    return render_template('index.html')

@web_bp.route('/stats')
@login_required
def stats():
    return render_template('index.html')

@web_bp.route('/settings')
@login_required
def settings():
    return render_template('index.html')

@web_bp.route('/info')
@login_required
def info():
    return render_template('index.html')

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('web.index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng')
    return render_template('login.html')

@web_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại')
            return redirect(url_for('web.signup'))
            
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('web.login'))
    return render_template('signup.html')

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công')
    return redirect(url_for('web.login')) 