from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models import User, StudentProfile, CompanyProfile, Job, Application
from app.utils import admin_required
from app.metrics import sync_gauges

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    total_applications = Application.query.count()
    placed_students = StudentProfile.query.filter_by(placement_status='placed').count()

    pending_companies = CompanyProfile.query.filter_by(approval_status='pending').all()
    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(8).all()

    sync_gauges()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_companies=total_companies,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_applications,
        placed_students=placed_students,
        pending_companies=pending_companies,
        recent_applications=recent_applications
    )


@admin_bp.route('/companies')
@admin_required
def companies():
    status_filter = request.args.get('status', 'all')
    query = CompanyProfile.query

    if status_filter in ['pending', 'approved', 'rejected']:
        query = query.filter_by(approval_status=status_filter)

    company_list = query.order_by(CompanyProfile.created_at.desc()).all()
    return render_template('admin/companies.html', companies=company_list, current_filter=status_filter)


@admin_bp.route('/companies/<int:company_id>/approve', methods=['POST'])
@admin_required
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'approved'
    db.session.commit()
    flash(f'Company "{company.company_name}" has been approved successfully.', 'success')
    return redirect(request.referrer or url_for('admin.companies'))


@admin_bp.route('/companies/<int:company_id>/reject', methods=['POST'])
@admin_required
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'Company "{company.company_name}" has been rejected.', 'warning')
    return redirect(request.referrer or url_for('admin.companies'))


@admin_bp.route('/companies/<int:company_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_company_status(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.user.is_active = not company.user.is_active
    db.session.commit()
    state = 'activated' if company.user.is_active else 'deactivated'
    flash(f'Company account "{company.company_name}" has been {state}.', 'info')
    return redirect(request.referrer or url_for('admin.companies'))


@admin_bp.route('/students')
@admin_required
def students():
    branch_filter = request.args.get('branch', '')
    status_filter = request.args.get('status', '')

    query = StudentProfile.query
    if branch_filter:
        query = query.filter(StudentProfile.branch == branch_filter)
    if status_filter:
        query = query.filter(StudentProfile.placement_status == status_filter)

    student_list = query.order_by(StudentProfile.created_at.desc()).all()
    branches = db.session.query(StudentProfile.branch).distinct().all()
    branch_options = [b[0] for b in branches if b[0]]

    return render_template(
        'admin/students.html',
        students=student_list,
        branch_options=branch_options,
        current_branch=branch_filter,
        current_status=status_filter
    )


@admin_bp.route('/students/<int:student_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_student_status(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student.user.is_active = not student.user.is_active
    db.session.commit()
    state = 'activated' if student.user.is_active else 'deactivated'
    flash(f'Student "{student.full_name}" has been {state}.', 'info')
    return redirect(request.referrer or url_for('admin.students'))


@admin_bp.route('/jobs')
@admin_required
def jobs():
    job_list = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('admin/jobs.html', jobs=job_list)


@admin_bp.route('/applications')
@admin_required
def applications():
    status_filter = request.args.get('status', '')
    query = Application.query
    if status_filter:
        query = query.filter(Application.status == status_filter)

    application_list = query.order_by(Application.applied_at.desc()).all()
    return render_template('admin/applications.html', applications=application_list, current_status=status_filter)
