from app.models import User, StudentProfile, CompanyProfile


def test_student_registration(client, db):
    """Test student registration creates User and StudentProfile with hashed password."""
    response = client.post('/auth/register/student', data={
        'full_name': 'Test Student',
        'email': 'student.test@campus.edu',
        'roll_number': 'CS22B001',
        'branch': 'Computer Science & Engineering',
        'cgpa': '8.2',
        'graduation_year': '2026',
        'phone': '+91 99999 88888',
        'skills': 'Python, Flask, Docker',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    user = User.query.filter_by(email='student.test@campus.edu').first()
    assert user is not None
    assert user.role == 'student'
    assert user.check_password('Password@123')
    assert not user.check_password('WrongPassword')
    assert user.student_profile is not None
    assert user.student_profile.roll_number == 'CS22B001'
    assert user.student_profile.cgpa == 8.2


def test_company_registration_pending(client, db):
    """Test company registration sets approval_status to pending."""
    response = client.post('/auth/register/company', data={
        'company_name': 'Innovate Inc',
        'email': 'hiring@innovate.com',
        'industry': 'Information Technology & Software',
        'website': 'https://innovate.com',
        'contact_person': 'Jane Doe',
        'phone': '+91 80 1234 5678',
        'description': 'AI & Cloud development.',
        'password': 'Company@123',
        'confirm_password': 'Company@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    company_user = User.query.filter_by(email='hiring@innovate.com').first()
    assert company_user is not None
    assert company_user.role == 'company'
    assert company_user.company_profile is not None
    assert company_user.company_profile.approval_status == 'pending'
    assert not company_user.company_profile.is_approved()


def test_login_success_and_logout(client, student_user):
    """Test valid user login redirects to dashboard and logout terminates session."""
    # Login
    response = client.post('/auth/login', data={
        'email': 'john.doe@campus.edu',
        'password': 'Student@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back, john.doe@campus.edu!' in response.data or b'Student Dashboard' in response.data

    # Logout
    logout_res = client.get('/auth/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b'logged out' in logout_res.data


def test_login_invalid_credentials(client, student_user):
    """Test invalid credentials display flash error message."""
    response = client.post('/auth/login', data={
        'email': 'john.doe@campus.edu',
        'password': 'IncorrectPassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_deactivated_user_blocked(client, db, student_user):
    """Test deactivated account is denied login."""
    student_user.is_active = False
    db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'john.doe@campus.edu',
        'password': 'Student@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'deactivated' in response.data.lower()
