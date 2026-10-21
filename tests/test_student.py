from datetime import datetime, timedelta, timezone
from app.models import Application, Job


def test_student_apply_flow(client, db, student_user, sample_job):
    """Test eligible student can successfully apply for an active job."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    response = client.post(f'/student/jobs/{sample_job.id}/apply', follow_redirects=True)
    assert response.status_code == 200
    assert b'Application submitted successfully' in response.data

    application = Application.query.filter_by(job_id=sample_job.id, student_id=student_user.student_profile.id).first()
    assert application is not None
    assert application.status == 'applied'


def test_duplicate_application_blocked(client, db, student_user, sample_job):
    """Test duplicate application for the same job is strictly blocked."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    # First application succeeds
    res1 = client.post(f'/student/jobs/{sample_job.id}/apply', follow_redirects=True)
    assert res1.status_code == 200

    # Second application is rejected
    res2 = client.post(f'/student/jobs/{sample_job.id}/apply', follow_redirects=True)
    assert res2.status_code == 200
    assert b'already applied' in res2.data.lower() or b'duplicate' in res2.data.lower()

    count = Application.query.filter_by(job_id=sample_job.id, student_id=student_user.student_profile.id).count()
    assert count == 1


def test_ineligible_cgpa_blocked(client, db, student_user, sample_job):
    """Test student with CGPA lower than job cutoff is blocked from applying."""
    # Set student CGPA to 6.5 (job cutoff is 7.5)
    student_user.student_profile.cgpa = 6.5
    db.session.commit()

    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})
    response = client.post(f'/student/jobs/{sample_job.id}/apply', follow_redirects=True)

    assert response.status_code == 200
    assert b'requirement not met' in response.data.lower() or b'cgpa' in response.data.lower()
    app = Application.query.filter_by(job_id=sample_job.id, student_id=student_user.student_profile.id).first()
    assert app is None


def test_expired_job_blocked(client, db, student_user, sample_job):
    """Test applying to an expired job is rejected."""
    # Set deadline in the past
    sample_job.deadline = datetime.now(timezone.utc) - timedelta(days=2)
    db.session.commit()

    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})
    response = client.post(f'/student/jobs/{sample_job.id}/apply', follow_redirects=True)

    assert response.status_code == 200
    assert b'expired' in response.data.lower()
    app = Application.query.filter_by(job_id=sample_job.id, student_id=student_user.student_profile.id).first()
    assert app is None
