import os
import pytest
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db as _db
from app.models import User, CompanyProfile, StudentProfile, Job, Application


@pytest.fixture(scope='session')
def app():
    """Create and configure a testing Flask app instance."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean database session per test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def admin_user(db):
    """Create a default admin user."""
    admin = User(email='admin@placement.com', role='admin', is_active=True)
    admin.set_password('Admin@123')
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def company_user(db):
    """Create an approved company user."""
    user = User(email='recruiter@techcorp.com', role='company', is_active=True)
    user.set_password('Company@123')
    db.session.add(user)
    db.session.flush()

    profile = CompanyProfile(
        user_id=user.id,
        company_name='TechCorp Global',
        industry='Information Technology & Software',
        approval_status='approved'
    )
    db.session.add(profile)
    db.session.commit()
    return user


@pytest.fixture
def pending_company_user(db):
    """Create an unapproved company user."""
    user = User(email='new@startup.io', role='company', is_active=True)
    user.set_password('Startup@123')
    db.session.add(user)
    db.session.flush()

    profile = CompanyProfile(
        user_id=user.id,
        company_name='New Startup',
        industry='Information Technology & Software',
        approval_status='pending'
    )
    db.session.add(profile)
    db.session.commit()
    return user


@pytest.fixture
def student_user(db):
    """Create an active student user with CGPA 8.5."""
    user = User(email='john.doe@campus.edu', role='student', is_active=True)
    user.set_password('Student@123')
    db.session.add(user)
    db.session.flush()

    profile = StudentProfile(
        user_id=user.id,
        full_name='John Doe',
        roll_number='CS21B999',
        branch='Computer Science & Engineering',
        cgpa=8.5,
        graduation_year=2026,
        skills='Python, Docker, SQL',
        placement_status='unplaced'
    )
    db.session.add(profile)
    db.session.commit()
    return user


@pytest.fixture
def sample_job(db, company_user):
    """Create an active job with cutoff CGPA 7.5."""
    now = datetime.now(timezone.utc)
    job = Job(
        company_id=company_user.company_profile.id,
        title='Software Engineer',
        description='Design and build distributed systems.',
        location='Bengaluru',
        package_lpa=16.0,
        required_skills='Python, SQL',
        min_cgpa=7.5,
        deadline=now + timedelta(days=20),
        is_active=True
    )
    db.session.add(job)
    db.session.commit()
    return job
