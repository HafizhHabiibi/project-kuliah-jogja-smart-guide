from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login berhasil.', 'success')
            if user.is_admin:
                return redirect(url_for('admin.index'))
            return redirect(url_for('dashboard.index'))
        else:
            flash('Email atau password salah.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or not email or not password:
            flash('Semua field harus diisi.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password minimal 6 karakter.', 'error')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email sudah terdaftar. Silakan login.', 'error')
            return render_template('register.html')

        # Get initial preferences (Nature, Culture, Culinary, Crowd, Effort)
        def get_pref_value(name):
            try:
                val = int(request.form.get(name, 3))
                return max(1, min(5, val))
            except (ValueError, TypeError):
                return 3

        pref_nature = get_pref_value('pref_nature')
        pref_culture = get_pref_value('pref_culture')
        pref_culinary = get_pref_value('pref_culinary')
        pref_crowd = get_pref_value('pref_crowd')
        pref_effort = get_pref_value('pref_effort')

        # Create new user
        new_user = User(
            username=username,
            email=email,
            pref_nature=pref_nature,
            pref_culture=pref_culture,
            pref_culinary=pref_culinary,
            pref_crowd=pref_crowd,
            pref_effort=pref_effort
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrasi berhasil.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout berhasil.', 'success')
    return redirect(url_for('dashboard.landing'))
