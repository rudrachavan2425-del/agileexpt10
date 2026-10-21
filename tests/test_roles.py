def test_admin_route_forbidden_for_student(client, student_user):
    """Test student cannot access admin dashboard (403 Forbidden)."""
    # Log in as student
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})
    response = client.get('/admin/dashboard')
    assert response.status_code == 403


def test_student_route_forbidden_for_company(client, company_user):
    """Test company cannot access student dashboard (403 Forbidden)."""
    client.post('/auth/login', data={'email': company_user.email, 'password': 'Company@123'})
    response = client.get('/student/dashboard')
    assert response.status_code == 403


def test_unauthenticated_redirect_to_login(client):
    """Test unauthenticated user accessing protected dashboard is redirected to login."""
    response = client.get('/admin/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers.get('Location', '')
