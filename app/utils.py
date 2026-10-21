import os
import uuid
from functools import wraps
from flask import abort, flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def role_required(*allowed_roles):
    """Decorator to enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if not current_user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return redirect(url_for('auth.logout'))
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return role_required('admin')(f)


def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_active:
            flash('Your account has been deactivated. Please contact the administrator.', 'danger')
            return redirect(url_for('auth.logout'))
        if not current_user.is_company():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    return role_required('student')(f)


def save_resume_file(file_storage):
    """Save an uploaded resume PDF securely and return unique filename."""
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if extension not in current_app.config['ALLOWED_EXTENSIONS']:
        return None

    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_storage.save(upload_path)
    return unique_filename
