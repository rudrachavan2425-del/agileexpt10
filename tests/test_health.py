def test_health_endpoint(client):
    """Test /health endpoint returns JSON status ok with HTTP 200."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data.get('status') == 'ok'


def test_metrics_endpoint(client):
    """Test /metrics endpoint returns prometheus metrics including custom metrics."""
    response = client.get('/metrics')
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    assert 'placement_registered_students_total' in content
    assert 'placement_active_jobs_total' in content
    assert 'flask_http_request_duration_seconds' in content or 'flask_http_request_total' in content
