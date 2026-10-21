import pytest

pytest_plugins = ["tests.conftest"]


from tests.test_health import test_health_endpoint, test_metrics_endpoint
from tests.test_auth import (
    test_student_registration,
    test_company_registration_pending,
    test_login_success_and_logout,
    test_login_invalid_credentials,
)
from tests.test_roles import (
    test_admin_route_forbidden_for_student,
    test_student_route_forbidden_for_company,
    test_unauthenticated_redirect_to_login,
)
from tests.test_company import (
    test_create_job,
    test_unapproved_company_cannot_create_job,
    test_edit_and_delete_job,
)
from tests.test_student import (
    test_student_apply_flow,
    test_duplicate_application_blocked,
    test_ineligible_cgpa_blocked,
    test_expired_job_blocked,
)
from tests.test_admin import (
    test_admin_dashboard_stats,
    test_admin_approve_and_reject_company,
    test_admin_toggle_user_status,
)


def test_home_page(client):
    """Verify home page loads successfully with HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Placement' in response.data or b'Campus' in response.data
