from app.models import CompanyProfile, StudentProfile


def test_admin_dashboard_stats(client, admin_user, sample_job):
    """Test admin dashboard loads with computed metrics."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Administrative Overview' in response.data
    assert b'Total Students' in response.data


def test_admin_approve_and_reject_company(client, db, admin_user, pending_company_user):
    """Test admin can approve and reject pending companies."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})
    comp_id = pending_company_user.company_profile.id

    # Approve
    res_app = client.post(f'/admin/companies/{comp_id}/approve', follow_redirects=True)
    assert res_app.status_code == 200
    db.session.refresh(pending_company_user.company_profile)
    assert pending_company_user.company_profile.approval_status == 'approved'

    # Reject
    res_rej = client.post(f'/admin/companies/{comp_id}/reject', follow_redirects=True)
    assert res_rej.status_code == 200
    db.session.refresh(pending_company_user.company_profile)
    assert pending_company_user.company_profile.approval_status == 'rejected'


def test_admin_toggle_user_status(client, db, admin_user, student_user, company_user):
    """Test admin can activate and deactivate student and company accounts."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})

    # Toggle student
    client.post(f'/admin/students/{student_user.student_profile.id}/toggle-status', follow_redirects=True)
    db.session.refresh(student_user)
    assert student_user.is_active is False

    client.post(f'/admin/students/{student_user.student_profile.id}/toggle-status', follow_redirects=True)
    db.session.refresh(student_user)
    assert student_user.is_active is True

    # Toggle company
    client.post(f'/admin/companies/{company_user.company_profile.id}/toggle-status', follow_redirects=True)
    db.session.refresh(company_user)
    assert company_user.is_active is False


def test_admin_view_jobs_and_applications(client, admin_user, sample_job):
    """Test admin jobs and applications listing views."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})

    res_jobs = client.get('/admin/jobs')
    assert res_jobs.status_code == 200
    assert b'Campus Placement Job Postings' in res_jobs.data

    res_apps = client.get('/admin/applications')
    assert res_apps.status_code == 200
    assert b'Placement Applications Audit' in res_apps.data
