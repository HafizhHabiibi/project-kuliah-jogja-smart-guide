import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def index():
    preferences = []
    if current_user.preferences:
        try:
            preferences = json.loads(current_user.preferences)
        except (json.JSONDecodeError, TypeError):
            preferences = []
    return render_template('profile.html', preferences=preferences)


@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def update():
    username = request.form.get('username', '').strip()
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    preferences = request.form.getlist('preferences')

    if username:
        current_user.username = username

    if new_password:
        if new_password != confirm_password:
            flash('Password baru dan konfirmasi tidak cocok.', 'error')
            return redirect(url_for('profile.index'))
        if len(new_password) < 6:
            flash('Password minimal 6 karakter.', 'error')
            return redirect(url_for('profile.index'))
        current_user.set_password(new_password)

    current_user.preferences = json.dumps(preferences)

    # Get initial preferences (Nature, Culture, Culinary, Crowd, Effort)
    def get_pref_value(name):
        try:
            val = int(request.form.get(name, 3))
            return max(1, min(5, val))
        except (ValueError, TypeError):
            return 3

    current_user.pref_nature = get_pref_value('pref_nature')
    current_user.pref_culture = get_pref_value('pref_culture')
    current_user.pref_culinary = get_pref_value('pref_culinary')
    current_user.pref_crowd = get_pref_value('pref_crowd')
    current_user.pref_effort = get_pref_value('pref_effort')

    db.session.commit()

    flash('Profil berhasil diperbarui.', 'success')
    return redirect(url_for('profile.index'))
