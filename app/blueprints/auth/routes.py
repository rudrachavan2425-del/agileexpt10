from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, StudentProfile, CompanyProfile
from app.forms import LoginForm, StudentRegistrationForm, CompanyRegistrationForm
from app.utils import save_resume_file
from app.metrics import record_login, sync_gauges

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_company():
            return redirect(url_for('company.dashboard'))
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                record_login(False)
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            record_login(True)
            flash(f'Welcome to Placement system v4.0 - LIVE DEMO, {user.email}!', 'success')

            next_page = request.args.get('next')

            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_company():
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            record_login(False)
            flash('Invalid email or password. Please verify your credentials.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    form = StudentRegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.strip().lower(),
            role='student',
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        resume_filename = None
        if form.resume.data:
            resume_filename = save_resume_file(form.resume.data)

        profile = StudentProfile(
            user_id=user.id,
            full_name=form.full_name.data.strip(),
            roll_number=form.roll_number.data.strip().upper(),
            branch=form.branch.data,
            cgpa=form.cgpa.data,
            graduation_year=form.graduation_year.data,
            phone=form.phone.data.strip() if form.phone.data else None,
            skills=form.skills.data.strip() if form.skills.data else None,
            resume_filename=resume_filename,
            placement_status='unplaced'
        )
        db.session.add(profile)
        db.session.commit()

        sync_gauges()
        flash('Registration successful! You can now log in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_student.html', form=form)


@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.strip().lower(),
            role='company',
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        profile = CompanyProfile(
            user_id=user.id,
            company_name=form.company_name.data.strip(),
            website=form.website.data.strip() if form.website.data else None,
            industry=form.industry.data,
            contact_person=form.contact_person.data.strip() if form.contact_person.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
            description=form.description.data.strip() if form.description.data else None,
            approval_status='pending'
        )
        db.session.add(profile)
        db.session.commit()

        flash('Company registration submitted! An administrator will review and approve your account shortly.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_company.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
