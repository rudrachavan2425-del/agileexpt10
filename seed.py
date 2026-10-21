"""Seed script for Placement Management System.

Populates the database with:
- 1 Admin: admin@placement.com / Admin@123
- 3 Companies (Approved)
- 10 Students (Various branches, CGPAs, and skills)
- 8 Job postings (Diverse roles, salary packages, and eligibility criteria)
- Multiple applications with diverse statuses (applied, shortlisted, selected, rejected)
"""

from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import User, CompanyProfile, StudentProfile, Job, Application
from app.metrics import sync_gauges, record_application


def seed_database():
    app = create_app('development')
    with app.app_context():
        print("[+] Dropping existing database tables...")
        db.drop_all()
        print("[+] Creating database schema...")
        db.create_all()

        # ---------------------------------------------------------
        # 1. Admin User
        # ---------------------------------------------------------
        print("[+] Seeding Admin account...")
        admin = User(
            email='admin@placement.com',
            role='admin',
            is_active=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

        # ---------------------------------------------------------
        # 2. 3 Companies
        # ---------------------------------------------------------
        print("[+] Seeding 3 Company profiles...")
        companies_data = [
            {
                'email': 'recruiting@google.com',
                'password': 'Company@123',
                'company_name': 'Google Cloud',
                'industry': 'Information Technology & Software',
                'website': 'https://cloud.google.com',
                'contact_person': 'Sundararajan HR',
                'phone': '+91 80 6789 0001',
                'description': 'Global leader in cloud computing, machine learning, and scalable enterprise services.'
            },
            {
                'email': 'careers@microsoft.com',
                'password': 'Company@123',
                'company_name': 'Microsoft Corporation',
                'industry': 'Information Technology & Software',
                'website': 'https://microsoft.com',
                'contact_person': 'Anita Sharma',
                'phone': '+91 40 4567 8900',
                'description': 'Empowering every person and every organization on the planet to achieve more with modern software & AI.'
            },
            {
                'email': 'campus@goldmansachs.com',
                'password': 'Company@123',
                'company_name': 'Goldman Sachs',
                'industry': 'Consulting & Financial Services',
                'website': 'https://goldmansachs.com',
                'contact_person': 'Rohan Sen',
                'phone': '+91 80 4123 5555',
                'description': 'Premier global investment banking, securities, and quantitative technology management firm.'
            }
        ]

        company_objects = []
        for c in companies_data:
            user = User(email=c['email'], role='company', is_active=True)
            user.set_password(c['password'])
            db.session.add(user)
            db.session.flush()

            profile = CompanyProfile(
                user_id=user.id,
                company_name=c['company_name'],
                industry=c['industry'],
                website=c['website'],
                contact_person=c['contact_person'],
                phone=c['phone'],
                description=c['description'],
                approval_status='approved'
            )
            db.session.add(profile)
            db.session.flush()
            company_objects.append(profile)

        # ---------------------------------------------------------
        # 3. 10 Students
        # ---------------------------------------------------------
        print("[+] Seeding 10 Student profiles...")
        students_data = [
            {
                'name': 'Aarav Sharma',
                'email': 'aarav.sharma@campus.edu',
                'roll': 'CS21B101',
                'branch': 'Computer Science & Engineering',
                'cgpa': 9.4,
                'year': 2026,
                'phone': '+91 98765 00001',
                'skills': 'Python, Go, Kubernetes, System Design, Algorithms'
            },
            {
                'name': 'Diya Patel',
                'email': 'diya.patel@campus.edu',
                'roll': 'IT21B102',
                'branch': 'Information Technology',
                'cgpa': 8.8,
                'year': 2026,
                'phone': '+91 98765 00002',
                'skills': 'React, Node.js, TypeScript, PostgreSQL, Docker'
            },
            {
                'name': 'Rohan Verma',
                'email': 'rohan.verma@campus.edu',
                'roll': 'CS21B103',
                'branch': 'Computer Science & Engineering',
                'cgpa': 7.6,
                'year': 2026,
                'phone': '+91 98765 00003',
                'skills': 'Java, Spring Boot, MySQL, REST APIs, Git'
            },
            {
                'name': 'Ananya Iyer',
                'email': 'ananya.iyer@campus.edu',
                'roll': 'AI21B104',
                'branch': 'Data Science & AI',
                'cgpa': 9.6,
                'year': 2026,
                'phone': '+91 98765 00004',
                'skills': 'PyTorch, Machine Learning, NLP, Python, Pandas, MLOps'
            },
            {
                'name': 'Kabir Nair',
                'email': 'kabir.nair@campus.edu',
                'roll': 'EC21B105',
                'branch': 'Electronics & Communication',
                'cgpa': 8.1,
                'year': 2026,
                'phone': '+91 98765 00005',
                'skills': 'Embedded C, IoT, Python, Circuit Design, Linux'
            },
            {
                'name': 'Sanya Malhotra',
                'email': 'sanya.m@campus.edu',
                'roll': 'CS21B106',
                'branch': 'Computer Science & Engineering',
                'cgpa': 8.9,
                'year': 2026,
                'phone': '+91 98765 00006',
                'skills': 'Go, AWS, Terraform, Docker, Microservices, Python'
            },
            {
                'name': 'Vikram Mehra',
                'email': 'vikram.m@campus.edu',
                'roll': 'EE21B107',
                'branch': 'Electrical Engineering',
                'cgpa': 7.2,
                'year': 2026,
                'phone': '+91 98765 00007',
                'skills': 'MATLAB, Python, Power Electronics, Automation'
            },
            {
                'name': 'Ishita Mukherjee',
                'email': 'ishita.m@campus.edu',
                'roll': 'IT21B108',
                'branch': 'Information Technology',
                'cgpa': 8.4,
                'year': 2026,
                'phone': '+91 98765 00008',
                'skills': 'Angular, NestJS, MongoDB, Express, Docker'
            },
            {
                'name': 'Devansh Gupta',
                'email': 'devansh.g@campus.edu',
                'roll': 'ME21B109',
                'branch': 'Mechanical Engineering',
                'cgpa': 7.9,
                'year': 2026,
                'phone': '+91 98765 00009',
                'skills': 'CAD/CAM, Python, Robotics, Finite Element Analysis'
            },
            {
                'name': 'Meera Rao',
                'email': 'meera.rao@campus.edu',
                'roll': 'AI21B110',
                'branch': 'Data Science & AI',
                'cgpa': 9.2,
                'year': 2026,
                'phone': '+91 98765 00010',
                'skills': 'Computer Vision, OpenCV, TensorFlow, Python, Docker'
            }
        ]

        student_objects = []
        for s in students_data:
            user = User(email=s['email'], role='student', is_active=True)
            user.set_password('Student@123')
            db.session.add(user)
            db.session.flush()

            profile = StudentProfile(
                user_id=user.id,
                full_name=s['name'],
                roll_number=s['roll'],
                branch=s['branch'],
                cgpa=s['cgpa'],
                graduation_year=s['year'],
                phone=s['phone'],
                skills=s['skills'],
                placement_status='unplaced'
            )
            db.session.add(profile)
            db.session.flush()
            student_objects.append(profile)

        # ---------------------------------------------------------
        # 4. 8 Jobs
        # ---------------------------------------------------------
        print("[+] Seeding 8 Job postings...")
        now = datetime.now(timezone.utc)
        jobs_data = [
            {
                'company': company_objects[0],  # Google Cloud
                'title': 'Cloud Infrastructure Software Engineer',
                'description': 'Design, build and optimize highly reliable, distributed cloud control planes and storage infrastructure.',
                'location': 'Bengaluru, India (Hybrid)',
                'package_lpa': 26.0,
                'skills': 'Python, Go, Distributed Systems, Linux, Kubernetes',
                'min_cgpa': 8.5,
                'deadline': now + timedelta(days=30),
                'is_active': True
            },
            {
                'company': company_objects[0],  # Google Cloud
                'title': 'Site Reliability Engineer (SRE)',
                'description': 'Ensure maximum availability, performance, and operational excellence for global tier-1 services.',
                'location': 'Hyderabad, India',
                'package_lpa': 22.0,
                'skills': 'Python, Linux, Shell Scripting, Docker, Monitoring, Prometheus',
                'min_cgpa': 8.0,
                'deadline': now + timedelta(days=25),
                'is_active': True
            },
            {
                'company': company_objects[0],  # Google Cloud
                'title': 'Machine Learning Platform Engineer',
                'description': 'Develop scalable distributed training and inference platforms for Gemini and large foundational models.',
                'location': 'Bengaluru, India',
                'package_lpa': 28.5,
                'skills': 'Python, PyTorch, C++, Distributed Systems, GPU Optimization',
                'min_cgpa': 9.0,
                'deadline': now + timedelta(days=20),
                'is_active': True
            },
            {
                'company': company_objects[1],  # Microsoft
                'title': 'Software Engineer - Azure Core',
                'description': 'Build hyper-scale cloud infrastructure, hypervisors, and software-defined networking components.',
                'location': 'Hyderabad, India (Hybrid)',
                'package_lpa': 24.0,
                'skills': 'C++, C#, Systems Programming, Cloud Architecture',
                'min_cgpa': 8.0,
                'deadline': now + timedelta(days=35),
                'is_active': True
            },
            {
                'company': company_objects[1],  # Microsoft
                'title': 'Full Stack Developer - Microsoft 365',
                'description': 'Create intuitive, responsive, and collaborative web experiences consumed by hundreds of millions of users.',
                'location': 'Bengaluru, India',
                'package_lpa': 18.0,
                'skills': 'TypeScript, React, Node.js, GraphQL, Azure',
                'min_cgpa': 7.5,
                'deadline': now + timedelta(days=40),
                'is_active': True
            },
            {
                'company': company_objects[1],  # Microsoft
                'title': 'Data & Applied Scientist',
                'description': 'Leverage cutting-edge generative AI models to transform enterprise productivity and search intelligence.',
                'location': 'Hyderabad, India',
                'package_lpa': 25.0,
                'skills': 'Python, Machine Learning, Deep Learning, Statistics, NLP',
                'min_cgpa': 8.5,
                'deadline': now + timedelta(days=15),
                'is_active': True
            },
            {
                'company': company_objects[2],  # Goldman Sachs
                'title': 'Quantitative Technology Analyst',
                'description': 'Develop algorithmic trading models, high-frequency execution pipelines, and risk engines.',
                'location': 'Bengaluru, India (On-site)',
                'package_lpa': 30.0,
                'skills': 'C++, Python, Mathematics, Financial Engineering, Multithreading',
                'min_cgpa': 8.5,
                'deadline': now + timedelta(days=28),
                'is_active': True
            },
            {
                'company': company_objects[2],  # Goldman Sachs
                'title': 'Cybersecurity & Application Security Associate',
                'description': 'Protect mission-critical financial assets with threat modeling, vulnerability management, and automated security scanning.',
                'location': 'Bengaluru, India',
                'package_lpa': 21.0,
                'skills': 'Python, Network Security, Cryptography, OWASP, Cloud Security',
                'min_cgpa': 7.5,
                'deadline': now + timedelta(days=22),
                'is_active': True
            }
        ]

        job_objects = []
        for j in jobs_data:
            job = Job(
                company_id=j['company'].id,
                title=j['title'],
                description=j['description'],
                location=j['location'],
                package_lpa=j['package_lpa'],
                required_skills=j['skills'],
                min_cgpa=j['min_cgpa'],
                deadline=j['deadline'],
                is_active=j['is_active']
            )
            db.session.add(job)
            db.session.flush()
            job_objects.append(job)

        # ---------------------------------------------------------
        # 5. Some Applications
        # ---------------------------------------------------------
        print("[+] Seeding student applications with diverse statuses...")
        # (student_index, job_index, status, feedback)
        applications_plan = [
            (0, 0, 'selected', 'Exceptional performance in systems design and distributed algorithms.'),
            (0, 6, 'shortlisted', 'Strong algorithmic background; scheduled for superday round.'),
            (3, 2, 'selected', 'Outstanding machine learning research portfolio and live coding session.'),
            (3, 5, 'applied', None),
            (1, 4, 'shortlisted', 'Good web development profile and portfolio projects.'),
            (5, 1, 'applied', None),
            (7, 4, 'applied', None),
            (9, 2, 'shortlisted', 'Impressive computer vision project demonstrations.'),
            (2, 7, 'rejected', 'Did not meet the prerequisite cryptography and security background.'),
            (4, 3, 'applied', None),
        ]

        for s_idx, j_idx, status, feedback in applications_plan:
            st = student_objects[s_idx]
            jb = job_objects[j_idx]

            app_obj = Application(
                job_id=jb.id,
                student_id=st.id,
                status=status,
                feedback=feedback,
                applied_at=now - timedelta(days=s_idx + 1)
            )
            db.session.add(app_obj)
            record_application(status=status)

            if status == 'selected':
                st.placement_status = 'placed'

        db.session.commit()
        sync_gauges()

        print("[✓] Database successfully seeded!")
        print("    Admin credentials: admin@placement.com / Admin@123")
        print("    Company credentials: recruiting@google.com / Company@123")
        print("    Student credentials: aarav.sharma@campus.edu / Student@123")


if __name__ == '__main__':
    seed_database()
