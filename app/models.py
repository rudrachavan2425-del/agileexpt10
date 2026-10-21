from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin', 'company', 'student'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_company(self) -> bool:
        return self.role == 'company'

    def is_student(self) -> bool:
        return self.role == 'student'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    contact_person = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(25), nullable=True)
    # 'pending', 'approved', 'rejected'
    approval_status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    jobs = db.relationship('Job', backref='company', cascade='all, delete-orphan', lazy='dynamic')

    def is_approved(self) -> bool:
        return self.approval_status == 'approved'

    def __repr__(self):
        return f'<CompanyProfile {self.company_name} status={self.approval_status}>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(25), nullable=True)
    # 'unplaced', 'placed'
    placement_status = db.Column(db.String(20), default='unplaced', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<StudentProfile {self.full_name} ({self.roll_number})>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    package_lpa = db.Column(db.Float, nullable=False)  # in Lakhs Per Annum (LPA) or Annual Salary
    required_skills = db.Column(db.String(255), nullable=False)
    min_cgpa = db.Column(db.Float, default=0.0, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    applications = db.relationship('Application', backref='job', cascade='all, delete-orphan', lazy='dynamic')

    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        deadline = self.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        return now > deadline

    def __repr__(self):
        return f'<Job {self.title} at {self.company.company_name if self.company else "Unknown"}>'


class Application(db.Model):
    __tablename__ = 'applications'
    __table_args__ = (
        db.UniqueConstraint('job_id', 'student_id', name='uq_job_student_application'),
    )

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    # 'applied', 'shortlisted', 'rejected', 'selected'
    status = db.Column(db.String(20), default='applied', nullable=False)
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    feedback = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Application Job={self.job_id} Student={self.student_id} Status={self.status}>'
