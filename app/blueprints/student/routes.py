import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_from_directory, current_app
from flask_login import current_user
from app.extensions import db
from app.models import Job, Application, StudentProfile
from app.forms import StudentProfileForm
from app.utils import student_required, save_resume_file
from app.metrics import record_application

student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/dashboard')
@student_required
def dashboard():
    profile = current_user.student_profile
    if not profile:
        abort(404)

    applications = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
    applied_job_ids = [a.job_id for a in applications]

    # Eligible jobs: active, deadline not passed, min_cgpa <= profile.cgpa, not already applied
    all_jobs = Job.query.filter_by(is_active=True).all()
    eligible_jobs = [
        j for j in all_jobs
        if not j.is_expired() and j.min_cgpa <= profile.cgpa and j.id not in applied_job_ids
    ][:5]

    return render_template(
        'student/dashboard.html',
        profile=profile,
        applications=applications,
        eligible_jobs=eligible_jobs
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    profile = current_user.student_profile
    form = StudentProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.full_name = form.full_name.data.strip()
        profile.branch = form.branch.data
        profile.cgpa = form.cgpa.data
        profile.graduation_year = form.graduation_year.data
        profile.phone = form.phone.data.strip() if form.phone.data else None
        profile.skills = form.skills.data.strip() if form.skills.data else None

        if form.resume.data:
            filename = save_resume_file(form.resume.data)
            if filename:
                profile.resume_filename = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', form=form, profile=profile)


@student_bp.route('/jobs')
@student_required
def jobs():
    profile = current_user.student_profile
    search_q = request.args.get('q', '').strip()
    location_filter = request.args.get('location', '').strip()
    eligible_only = request.args.get('eligible_only') == '1'

    query = Job.query.filter_by(is_active=True)
    if search_q:
        pattern = f'%{search_q}%'
        query = query.filter(
            Job.title.ilike(pattern) |
            Job.required_skills.ilike(pattern) |
            Job.description.ilike(pattern)
        )
    if location_filter:
        query = query.filter(Job.location.ilike(f'%{location_filter}%'))

    job_list = query.order_by(Job.created_at.desc()).all()

    if eligible_only:
        job_list = [j for j in job_list if not j.is_expired() and j.min_cgpa <= profile.cgpa]

    applied_job_ids = {a.job_id for a in Application.query.filter_by(student_id=profile.id).all()}

    return render_template(
        'student/jobs.html',
        jobs=job_list,
        applied_job_ids=applied_job_ids,
        profile=profile,
        search_q=search_q,
        location_filter=location_filter,
        eligible_only=eligible_only
    )


@student_bp.route('/jobs/<int:job_id>')
@student_required
def job_details(job_id):
    profile = current_user.student_profile
    job = Job.query.get_or_404(job_id)
    application = Application.query.filter_by(job_id=job.id, student_id=profile.id).first()
    is_eligible = (not job.is_expired()) and (profile.cgpa >= job.min_cgpa)

    return render_template(
        'student/job_details.html',
        job=job,
        application=application,
        is_eligible=is_eligible,
        profile=profile
    )


@student_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@student_required
def apply_job(job_id):
    profile = current_user.student_profile
    job = Job.query.get_or_404(job_id)

    # 1. Check if job is active
    if not job.is_active:
        flash('This job posting is currently inactive and not accepting applications.', 'danger')
        return redirect(url_for('student.job_details', job_id=job.id))

    # 2. Check if deadline passed
    if job.is_expired():
        flash('The application deadline for this job has expired.', 'danger')
        return redirect(url_for('student.job_details', job_id=job.id))

    # 3. Check CGPA eligibility
    if profile.cgpa < job.min_cgpa:
        flash(f'Eligibility requirement not met: minimum CGPA required is {job.min_cgpa}, your CGPA is {profile.cgpa}.', 'danger')
        return redirect(url_for('student.job_details', job_id=job.id))

    # 4. Check for duplicate application
    existing_app = Application.query.filter_by(job_id=job.id, student_id=profile.id).first()
    if existing_app:
        flash('You have already applied for this job. Duplicate applications are blocked.', 'warning')
        return redirect(url_for('student.job_details', job_id=job.id))

    # Create application
    application = Application(
        job_id=job.id,
        student_id=profile.id,
        status='applied'
    )
    db.session.add(application)
    db.session.commit()

    record_application(status='applied')
    flash(f'Application submitted successfully for {job.title} at {job.company.company_name}!', 'success')
    return redirect(url_for('student.applications'))


@student_bp.route('/applications')
@student_required
def applications():
    profile = current_user.student_profile
    my_applications = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
    return render_template('student/applications.html', applications=my_applications)


@student_bp.route('/resumes/<path:filename>')
def download_resume(filename):
    # Allowed for logged in users (admin, company viewing applicant, or student)
    if not current_user.is_authenticated:
        abort(401)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename, as_attachment=False)
