from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge, Counter

# Application factory compatible exporter
metrics = PrometheusMetrics.for_app_factory()

# Custom Business Metrics
registered_students_gauge = Gauge(
    'placement_registered_students_total',
    'Total count of registered students in the system'
)

active_jobs_gauge = Gauge(
    'placement_active_jobs_total',
    'Total count of active job postings available for applications'
)

applications_counter = Counter(
    'placement_applications_total',
    'Total job applications submitted, partitioned by status',
    ['status']
)

logins_counter = Counter(
    'placement_logins_total',
    'Total user login attempts, partitioned by success or failure',
    ['status']
)


def sync_gauges():
    """Sync gauges directly with the current database state."""
    try:
        from app.models import StudentProfile, Job
        student_count = StudentProfile.query.count()
        registered_students_gauge.set(student_count)

        active_job_count = Job.query.filter_by(is_active=True).count()
        active_jobs_gauge.set(active_job_count)
    except Exception:
        # Fallback if DB table is not ready yet during migration/init
        pass


def record_login(success: bool):
    """Record login metric."""
    status = 'success' if success else 'failure'
    logins_counter.labels(status=status).inc()


def record_application(status: str = 'applied'):
    """Record application metric."""
    applications_counter.labels(status=status).inc()
