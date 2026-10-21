from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from app.extensions import db
from app.models import Job, Application, StudentProfile
from app.forms import JobForm, ApplicationStatusUpdateForm
from app.utils import company_required
from app.metrics import sync_gauges

company_bp = Blueprint('company', __name__, url_prefix='/company')


@company_bp.route('/dashboard')
@company_required
def dashboard():
    profile = current_user.company_profile
    if not profile:
        abort(404)

    jobs = Job.query.filter_by(company_id=profile.id).order_by(Job.created_at.desc()).all()
    job_ids = [j.id for j in jobs]

    total_applications = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted_count = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'shortlisted'
    ).count() if job_ids else 0
    selected_count = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'selected'
    ).count() if job_ids else 0

    return render_template(
        'company/dashboard.html',
        profile=profile,
        jobs=jobs,
        total_applications=total_applications,
        shortlisted_count=shortlisted_count,
        selected_count=selected_count
    )


@company_bp.route('/jobs/new', methods=['GET', 'POST'])
@company_required
def create_job():
    profile = current_user.company_profile
    if not profile or not profile.is_approved():
        flash('Your company registration is pending approval by the administrator. You cannot post jobs yet.', 'warning')
        return redirect(url_for('company.dashboard'))

    form = JobForm()
    if form.validate_on_submit():
        # Combine date with end of day time
        deadline_date = form.deadline.data
        deadline_dt = datetime(deadline_date.year, deadline_date.month, deadline_date.day, 23, 59, 59, tzinfo=timezone.utc)

        job = Job(
            company_id=profile.id,
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            location=form.location.data.strip(),
            package_lpa=form.package_lpa.data,
            required_skills=form.required_skills.data.strip(),
            min_cgpa=form.min_cgpa.data,
            deadline=deadline_dt,
            is_active=form.is_active.data
        )
        db.session.add(job)
        db.session.commit()

        sync_gauges()
        flash(f'Job posting "{job.title}" created successfully!', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/job_form.html', form=form, title='Create New Job Posting')


@company_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@company_required
def edit_job(job_id):
    profile = current_user.company_profile
    job = Job.query.filter_by(id=job_id, company_id=profile.id).first_or_404()

    form = JobForm(obj=job)
    if request.method == 'GET':
        form.deadline.data = job.deadline.date()

    if form.validate_on_submit():
        deadline_date = form.deadline.data
        deadline_dt = datetime(deadline_date.year, deadline_date.month, deadline_date.day, 23, 59, 59, tzinfo=timezone.utc)

        job.title = form.title.data.strip()
        job.description = form.description.data.strip()
        job.location = form.location.data.strip()
        job.package_lpa = form.package_lpa.data
        job.required_skills = form.required_skills.data.strip()
        job.min_cgpa = form.min_cgpa.data
        job.deadline = deadline_dt
        job.is_active = form.is_active.data

        db.session.commit()
        sync_gauges()
        flash(f'Job "{job.title}" updated successfully.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/job_form.html', form=form, title=f'Edit Job: {job.title}', job=job)


@company_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@company_required
def delete_job(job_id):
    profile = current_user.company_profile
    job = Job.query.filter_by(id=job_id, company_id=profile.id).first_or_404()
    title = job.title
    db.session.delete(job)
    db.session.commit()

    sync_gauges()
    flash(f'Job posting "{title}" deleted successfully.', 'info')
    return redirect(url_for('company.dashboard'))


@company_bp.route('/jobs/<int:job_id>/toggle', methods=['POST'])
@company_required
def toggle_job(job_id):
    profile = current_user.company_profile
    job = Job.query.filter_by(id=job_id, company_id=profile.id).first_or_404()
    job.is_active = not job.is_active
    db.session.commit()

    sync_gauges()
    status = 'activated' if job.is_active else 'deactivated'
    flash(f'Job "{job.title}" has been {status}.', 'info')
    return redirect(url_for('company.dashboard'))


@company_bp.route('/jobs/<int:job_id>/applicants')
@company_required
def applicants(job_id):
    profile = current_user.company_profile
    job = Job.query.filter_by(id=job_id, company_id=profile.id).first_or_404()

    status_filter = request.args.get('status', 'all')
    query = Application.query.filter_by(job_id=job.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    applications = query.order_by(Application.applied_at.desc()).all()
    form = ApplicationStatusUpdateForm()

    return render_template('company/applicants.html', job=job, applications=applications, form=form, current_filter=status_filter)


@company_bp.route('/applications/<int:app_id>/status', methods=['POST'])
@company_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    if application.job.company_id != current_user.company_profile.id:
        abort(403)

    form = ApplicationStatusUpdateForm()
    if form.validate_on_submit():
        new_status = form.status.data
        application.status = new_status
        if form.feedback.data:
            application.feedback = form.feedback.data.strip()

        # If candidate is selected, optionally mark placement status as placed
        if new_status == 'selected':
            application.student.placement_status = 'placed'

        db.session.commit()
        flash(f'Applicant status updated to "{new_status.title()}".', 'success')

    return redirect(url_for('company.applicants', job_id=application.job_id))
