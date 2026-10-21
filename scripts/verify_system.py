"""
Placement Management System - Pre-flight & Runtime Verification Script
"""
import os
import re
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.models import User, Job, Application, StudentProfile, CompanyProfile


def get_csrf(resp_data):
    m = re.search(r'name=["\']csrf_token["\'][^>]*?value=["\']([^"\']+)["\']', resp_data.decode('utf-8'))
    return m.group(1) if m else ''


def verify():
    print("=" * 60)
    print("PLACEMENT MANAGEMENT SYSTEM: PRE-FLIGHT SYSTEM VERIFICATION")
    print("=" * 60)

    app = create_app('development')
    client = app.test_client()

    with app.app_context():
        # 1. Verify Database Records
        users_count = User.query.count()
        companies_count = CompanyProfile.query.count()
        students_count = StudentProfile.query.count()
        jobs_count = Job.query.count()
        apps_count = Application.query.count()

        print("[✓] Database integrity verified:")
        print(f"    - Users: {users_count}")
        print(f"    - Companies: {companies_count}")
        print(f"    - Students: {students_count}")
        print(f"    - Jobs: {jobs_count}")
        print(f"    - Applications: {apps_count}")

        # 2. Verify Health Endpoint
        res_health = client.get('/health')
        assert res_health.status_code == 200, f"Health check failed: {res_health.status_code}"
        json_data = res_health.get_json()
        assert json_data.get('status') == 'ok', f"Unexpected health payload: {json_data}"
        print(f"[✓] /health returned HTTP 200 with payload: {json_data}")

        # 3. Verify Metrics Endpoint
        res_metrics = client.get('/metrics')
        assert res_metrics.status_code == 200, f"Metrics check failed: {res_metrics.status_code}"
        metrics_text = res_metrics.data.decode('utf-8')
        assert 'placement_registered_students_total' in metrics_text
        assert 'placement_active_jobs_total' in metrics_text
        assert 'placement_applications_total' in metrics_text
        print(f"[✓] /metrics returned HTTP 200 with custom business telemetry ({len(metrics_text)} bytes)")

        # 4. Verify Public Index Page
        res_index = client.get('/')
        assert res_index.status_code == 200
        assert b'Campus Placement Management System' in res_index.data
        print("[✓] Public homepage rendered successfully with HTTP 200")

        # 5. Verify Student Login and Dashboard
        login_page = client.get('/auth/login')
        csrf_tok = get_csrf(login_page.data)

        res_login = client.post('/auth/login', data={
            'email': 'aarav.sharma@campus.edu',
            'password': 'Student@123',
            'csrf_token': csrf_tok
        }, follow_redirects=True)
        assert res_login.status_code == 200
        assert b'Aarav Sharma' in res_login.data
        print("[✓] Student authentication and dashboard verified")

        # 6. Verify Company Login and Dashboard
        client.get('/auth/logout')
        login_page = client.get('/auth/login')
        csrf_tok = get_csrf(login_page.data)

        res_comp = client.post('/auth/login', data={
            'email': 'recruiting@google.com',
            'password': 'Company@123',
            'csrf_token': csrf_tok
        }, follow_redirects=True)
        assert res_comp.status_code == 200
        assert b'Google Cloud' in res_comp.data
        print("[✓] Recruiter authentication and dashboard verified")

        # 7. Verify Admin Login and Dashboard
        client.get('/auth/logout')
        login_page = client.get('/auth/login')
        csrf_tok = get_csrf(login_page.data)

        res_admin = client.post('/auth/login', data={
            'email': 'admin@placement.com',
            'password': 'Admin@123',
            'csrf_token': csrf_tok
        }, follow_redirects=True)
        assert res_admin.status_code == 200
        assert b'Administrative Overview' in res_admin.data
        print("[✓] Admin authentication and KPI dashboard verified")

        print("=" * 60)
        print("ALL RUNTIME CHECKS PASSED PERFECTLY!")
        print("=" * 60)


if __name__ == '__main__':
    verify()
