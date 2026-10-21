from datetime import date, timedelta
from app.models import Job, Application


def test_create_job(client, company_user):
    """Test approved company can create a new job posting."""
    client.post('/auth/login', data={'email': company_user.email, 'password': 'Company@123'})
    deadline_str = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')

    response = client.post('/company/jobs/new', data={
        'title': 'Frontend Engineer',
        'description': 'Build responsive interfaces with React and Next.js.',
        'location': 'Remote',
        'package_lpa': '14.0',
        'required_skills': 'React, TypeScript, CSS',
        'min_cgpa': '7.0',
        'deadline': deadline_str,
        'is_active': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    job = Job.query.filter_by(title='Frontend Engineer').first()
    assert job is not None
    assert job.package_lpa == 14.0
    assert job.min_cgpa == 7.0
    assert job.company_id == company_user.company_profile.id


def test_unapproved_company_cannot_create_job(client, pending_company_user):
    """Test company with pending approval is redirected and blocked from posting jobs."""
    client.post('/auth/login', data={'email': pending_company_user.email, 'password': 'Startup@123'})
    response = client.get('/company/jobs/new', follow_redirects=True)
    assert response.status_code == 200
    assert b'pending approval' in response.data


def test_edit_and_delete_job(client, db, company_user, sample_job):
    """Test company can update and delete an existing job posting."""
    client.post('/auth/login', data={'email': company_user.email, 'password': 'Company@123'})
    deadline_str = (date.today() + timedelta(days=45)).strftime('%Y-%m-%d')

    # Edit
    edit_res = client.post(f'/company/jobs/{sample_job.id}/edit', data={
        'title': 'Senior Software Engineer',
        'description': 'Updated description.',
        'location': 'Hybrid',
        'package_lpa': '20.0',
        'required_skills': 'Python, Kubernetes',
        'min_cgpa': '8.0',
        'deadline': deadline_str,
        'is_active': 'y'
    }, follow_redirects=True)
    assert edit_res.status_code == 200

    updated = Job.query.get(sample_job.id)
    assert updated.title == 'Senior Software Engineer'
    assert updated.package_lpa == 20.0

    # Delete
    del_res = client.post(f'/company/jobs/{sample_job.id}/delete', follow_redirects=True)
    assert del_res.status_code == 200
    assert Job.query.get(sample_job.id) is None


def test_evaluate_applicant(client, db, company_user, student_user, sample_job):
    """Test company can shortlist and select a candidate, marking student as placed."""
    client.post('/auth/login', data={'email': company_user.email, 'password': 'Company@123'})

    app = Application(job_id=sample_job.id, student_id=student_user.student_profile.id, status='applied')
    db.session.add(app)
    db.session.commit()

    # Shortlist
    res1 = client.post(f'/company/applications/{app.id}/status', data={
        'status': 'shortlisted',
        'feedback': 'Good problem solving skills.'
    }, follow_redirects=True)
    assert res1.status_code == 200
    db.session.refresh(app)
    assert app.status == 'shortlisted'

    # Select candidate
    res2 = client.post(f'/company/applications/{app.id}/status', data={
        'status': 'selected',
        'feedback': 'Offer extended!'
    }, follow_redirects=True)
    assert res2.status_code == 200
    db.session.refresh(app)
    db.session.refresh(student_user.student_profile)
    assert app.status == 'selected'
    assert student_user.student_profile.placement_status == 'placed'
