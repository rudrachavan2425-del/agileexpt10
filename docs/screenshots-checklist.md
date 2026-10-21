# Lab Report & Project Submission: Screenshots Checklist

Use this checklist to capture and organize all mandatory screenshots for your project report, submission documentation, and viva evaluation.

---

## 1. GitHub Repository Screenshots
- [ ] **1.1 Repository Homepage**: Show the repository (`rudrachavan2425-del/agileexpt10.git`) with root directory structure, README banner, badges, and file list (`app/`, `Dockerfile`, `Jenkinsfile`, `docker-compose.yml`, `prometheus/`, `grafana/`).
- [ ] **1.2 Commit History**: Click on **Commits** showing clean, descriptive semantic git commits (`feat(core)`, `feat(monitoring)`, `feat(devops)`, `docs`).
- [ ] **1.3 Source Code View**: Code viewer screenshot of `Jenkinsfile`, `Dockerfile`, or `app/metrics.py`.

---

## 2. Automated Testing (Pytest) Screenshots
- [ ] **2.1 Pytest Execution Terminal**: Terminal run showing all 22 tests passing:
  ```bash
  pytest -v --cov=app
  ```
  Capture the green output showing:
  `============================== 22 passed in 9.01s ==============================`
- [ ] **2.2 Test Source Code**: Screenshot of test files in IDE or GitHub (`tests/test_student.py`, `tests/test_auth.py`, `tests/test_company.py`).
- [ ] **2.3 Test Results XML / Coverage**: Generated `coverage.xml` and `test-results.xml` artifacts.
- [ ] **2.4 Postman API Collection (Optional)**: Postman request test run verifying `/health` and `/metrics` returning HTTP 200.

---

## 3. Jenkins CI/CD Pipeline Screenshots
- [ ] **3.1 Declarative Pipeline Overview**: Jenkins Pipeline Stage View showing all 8 stages in green:
  - `Stage 1: Checkout`
  - `Stage 2: Install Dependencies`
  - `Stage 3: Build & Lint`
  - `Stage 4: Automated Tests`
  - `Stage 5: Docker Build`
  - `Stage 6: Docker Hub Push`
  - `Stage 7: Deploy`
  - `Stage 8: Smoke Test`
- [ ] **3.2 Console Output (Build Success)**: End of Jenkins console log displaying:
  `✓ CI/CD PIPELINE SUCCEEDED: ALL STAGES PASSED CLEANLY` and `Finished: SUCCESS`.
- [ ] **3.3 Quality Gate Enforcement (Viva Proof)**: Screenshot demonstrating that if a test fails in Stage 4, execution halts immediately and Stage 5 (Docker Build) and Stage 7 (Deploy) are NOT executed.

---

## 4. Docker & Containerization Screenshots
- [ ] **4.1 Docker Images**: Terminal output of `docker images` showing:
  - `placement-management-web`
  - `prom/prometheus`
  - `grafana/grafana`
  - `prom/node-exporter`
  - `placement-jenkins`
- [ ] **4.2 Running Containers**: Terminal output of `docker ps` or Docker Desktop showing active containers:
  - `placement_web` (5000->5000)
  - `placement_prometheus` (9090->9090)
  - `placement_grafana` (3000->3000)
  - `placement_node_exporter` (9100->9100)
  - `placement_jenkins` (8080->8080)
- [ ] **4.3 Docker Hub Repository**: Docker Hub web portal showing public repository with tags `latest` and `v<BUILD_NUMBER>`.

---

## 5. Application UI Screenshots
- [ ] **5.1 Public Landing Page**: `http://localhost:5000` showing hero banner, stats counter, and active job opportunities.
- [ ] **5.2 Student Dashboard**: Logged in as `aarav.sharma@campus.edu` showing profile, eligibility tracker, and applied jobs.
- [ ] **5.3 Job Application Flow**: Student applying for an active job with CGPA and deadline validation.
- [ ] **5.4 Duplicate Application Blocked**: Alert banner displaying error when applying twice to the same job opening.
- [ ] **5.5 Recruiter Dashboard**: Logged in as `recruiting@google.com` displaying applicant list, status controls (Shortlist/Reject/Select), and job creator form.
- [ ] **5.6 Administrative Overview**: Logged in as `admin@placement.com` showing system-wide statistics, company approval buttons, and user toggle switches.

---

## 6. Prometheus Monitoring Screenshots
- [ ] **6.1 Prometheus Targets**: `http://localhost:9090/targets` displaying:
  - `placement_app` (`web:5000/metrics`) - **State: UP (1/1)**
  - `node_exporter` (`node-exporter:9100/metrics`) - **State: UP (1/1)**
- [ ] **6.2 Prometheus Raw Telemetry**: `http://localhost:5000/metrics` displaying raw Prometheus metrics exposition.
- [ ] **6.3 Prometheus PromQL Query Graph**: `http://localhost:9090/graph` running:
  - `sum(rate(flask_http_request_total[1m]))`
  - `placement_registered_students_total`

---

## 7. Grafana Dashboard Screenshots
- [ ] **7.1 Full DevOps Dashboard Overview**: `http://localhost:3000` showing **Placement Management System - DevOps & Business Analytics**.
- [ ] **7.2 Host Resource Telemetry**: Panels displaying:
  - Host CPU Usage (%) gauge
  - Memory Usage (%) gauge
  - Disk Usage (%) gauge
  - Network Traffic Inbound/Outbound graph
- [ ] **7.3 Application Performance Metrics**:
  - Application Availability (UP/DOWN indicator)
  - Requests per Second (req/s)
  - HTTP Status Code distribution
  - Average & p95 Response Latency
- [ ] **7.4 Business Metrics Panels**:
  - Registered Students counter
  - Active Jobs counter
  - Applications by Status pie chart
  - Login Success vs Failure pie chart

---

## 8. Prometheus Alerting Screenshots
- [ ] **8.1 Configured Alert Rules**: `http://localhost:9090/alerts` showing rules loaded from `alert.rules.yml`:
  - `ApplicationDown`
  - `HighCpuUsage`
  - `HighHttp5xxErrors`
  - `HighLatency`
- [ ] **8.2 Triggered Alert (FIRING)**:
  - Stop the web container: `docker stop placement_web`
  - Screenshot `http://localhost:9090/alerts` showing `ApplicationDown` in **FIRING (Red)** state.
  - Restart container `docker start placement_web` and capture auto-recovery to **INACTIVE (Green)**.
