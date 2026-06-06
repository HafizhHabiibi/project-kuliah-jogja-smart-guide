import os
import json
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.destination import Destination
from models.user import User

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Decorator that ensures the user is authenticated and is an admin."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Akses ditolak. Anda bukan admin.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin')
@admin_required
def index():
    """Admin dashboard — statistics and destination list."""
    destinations = Destination.query.all()
    total_destinations = len(destinations)
    categories = set(d.category for d in destinations)
    total_categories = len(categories)
    total_users = User.query.filter_by(is_admin=False).count()

    return render_template(
        'admin_dashboard.html',
        destinations=destinations,
        total_destinations=total_destinations,
        total_categories=total_categories,
        total_users=total_users
    )


@admin_bp.route('/admin/destination/add', methods=['GET', 'POST'])
@admin_required
def add_destination():
    """Add a new destination with full parameter scoring."""
    if request.method == 'POST':
        return _save_destination(None)
    return render_template('admin_destination_form.html', destination=None, editing=False)


@admin_bp.route('/admin/destination/edit/<int:dest_id>', methods=['GET', 'POST'])
@admin_required
def edit_destination(dest_id):
    """Edit an existing destination."""
    destination = Destination.query.get_or_404(dest_id)
    if request.method == 'POST':
        return _save_destination(destination)
    return render_template('admin_destination_form.html', destination=destination, editing=True)


@admin_bp.route('/admin/destination/delete/<int:dest_id>', methods=['POST'])
@admin_required
def delete_destination(dest_id):
    """Delete a destination."""
    destination = Destination.query.get_or_404(dest_id)
    name = destination.name
    db.session.delete(destination)
    db.session.commit()
    flash(f'Destinasi "{name}" berhasil dihapus.', 'success')
    return redirect(url_for('admin.index'))


@admin_bp.route('/admin/api/scrape-price')
@admin_required
def scrape_price():
    """Trigger price scraper for a given destination name query."""
    name = request.args.get('name', '').strip()
    if not name:
        return {'success': False, 'message': 'Nama tempat wisata tidak boleh kosong.'}, 400
        
    try:
        from services.price_scraper_service import find_scraper_by_name
        scraper_func = find_scraper_by_name(name)
        price, source = scraper_func()
        if price is not None:
            return {
                'success': True,
                'price': price,
                'source': source
            }
        else:
            return {
                'success': False,
                'message': 'Harga tiket masuk tidak ditemukan secara otomatis.'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error scraping: {str(e)}'
        }


def _save_destination(destination):

    """Save (create or update) a destination from form data."""
    # Basic info
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()

    try:
        latitude = float(request.form.get('latitude', 0))
        longitude = float(request.form.get('longitude', 0))
        rating = float(request.form.get('rating', 0))
        price = int(request.form.get('price', 0))
    except (ValueError, TypeError):
        flash('Data koordinat, rating, atau harga tidak valid.', 'error')
        return redirect(request.url)

    # Validation
    if not name or not description or not category:
        flash('Nama, deskripsi, dan kategori wajib diisi.', 'error')
        return redirect(request.url)

    # Handle photo upload
    photo_url = request.form.get('existing_photo_url', '')
    photo = request.files.get('photo')
    if photo and photo.filename and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        # Add timestamp prefix for uniqueness
        import time
        filename = f"{int(time.time())}_{filename}"
        upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'destinations')
        os.makedirs(upload_dir, exist_ok=True)
        photo.save(os.path.join(upload_dir, filename))
        photo_url = f'/static/images/destinations/{filename}'
    elif not photo_url and destination is None:
        flash('Foto destinasi wajib diupload.', 'error')
        return redirect(request.url)

    # Helper for score fields
    def get_score(field_name, default=3):
        try:
            val = int(request.form.get(field_name, default))
            return max(1, min(5, val))
        except (ValueError, TypeError):
            return default

    # Helper for multi-select fields
    def get_multi(field_name):
        values = request.form.getlist(field_name)
        return json.dumps(values)

    if destination is None:
        destination = Destination()
        db.session.add(destination)
        is_new = True
    else:
        is_new = False

    # Set basic fields
    destination.name = name
    destination.description = description
    destination.category = category
    destination.latitude = latitude
    destination.longitude = longitude
    destination.rating = rating
    destination.price = price
    if photo_url:
        destination.photo_url = photo_url

    # Nature parameters
    destination.nature_visual = get_score('nature_visual', 3)
    destination.nature_activities = get_multi('nature_activities')
    destination.nature_elements = get_multi('nature_elements')

    # Crowd parameters
    destination.crowd_review_count = get_score('crowd_review_count', 1)
    destination.crowd_rating = get_score('crowd_rating', 3)
    destination.crowd_hashtag = get_score('crowd_hashtag', 1)
    destination.crowd_activities = get_multi('crowd_activities')
    destination.crowd_facilities = get_multi('crowd_facilities')

    # Culinary parameters
    destination.culinary_facilities = get_multi('culinary_facilities')
    destination.culinary_activities = get_multi('culinary_activities')
    destination.culinary_types = get_multi('culinary_types')

    # Culture parameters
    destination.culture_heritage = get_multi('culture_heritage')
    destination.culture_activities = get_multi('culture_activities')
    destination.culture_elements = get_multi('culture_elements')

    # Effort parameters
    destination.effort_accessibility = get_multi('effort_accessibility')
    destination.effort_effort = get_multi('effort_effort')
    destination.effort_mobility = get_multi('effort_mobility')

    # Calculate MCDM scores automatically
    destination.update_dna_scores()

    db.session.commit()

    if is_new:
        flash(f'Destinasi "{name}" berhasil ditambahkan.', 'success')
    else:
        flash(f'Destinasi "{name}" berhasil diperbarui.', 'success')
    return redirect(url_for('admin.index'))
