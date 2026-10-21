# End-to-End DevOps Pipeline: 12-Step Demonstration Script

This document details the exact 12-step demonstration flow for viva, lab evaluations, and project presentations for the **Campus Placement Management System** DevOps pipeline.

---

## Complete Pipeline Architecture Flow
$$\text{Developer} \longrightarrow \text{Git Push} \longrightarrow \text{GitHub} \xrightarrow{\text{Webhook}} \text{Jenkins} \longrightarrow \text{Pytest Quality Gate} \longrightarrow \text{Docker Build} \longrightarrow \text{Docker Hub} \longrightarrow \text{Deploy} \longrightarrow \text{Prometheus} \longrightarrow \text{Grafana} \longrightarrow \text{Alerting}$$

---

## Step-by-Step Demonstration Execution

### Step 1: Developer Modifies Source Code Locally
Make a visible change or add a feature in the application code.
- Example: Open `app/templates/index.html` or `run.py` and update the brand banner or footer message:
  ```html
  <span class="badge bg-success">v2.1 Production Release - DevOps Automated</span>
  ```

### Step 2: Push Changes to GitHub
Commit the modification with a descriptive semantic commit message and push to GitHub:
```bash
git add .
git commit -m "feat(ui): update landing banner to v2.1"
git push origin main
```

### Step 3: GitHub Webhook Triggers Jenkins
- GitHub sends a real-time `push` event webhook payload to `http://<your-public-ip-or-ngrok>/github-webhook/`.
- Alternatively, Jenkins SCM Polling (`pollSCM('H/2 * * * *')`) detects the new commit within 120 seconds.
- Jenkins automatically initializes a new pipeline build: **Build #X**.

### Step 4: Jenkins Executes Stages (Checkout & Dependency Setup)
In the Jenkins Web UI (`http://localhost:8080/job/placement-pipeline`), observe the real-time execution:
- **Stage 1 (Checkout)**: Clones the latest commit from `rudrachavan2425-del/agileexpt10.git`.
- **Stage 2 (Install Dependencies)**: Creates Python 3 virtual environment and installs dependencies from `requirements.txt`.
- **Stage 3 (Build & Lint)**: Executes `flake8` static code analysis.

### Step 5: Automated Testing Quality Gate (Pytest)
- **Stage 4 (Automated Tests)**: Runs the complete test suite:
  ```bash
  pytest -v --cov=app --cov-report=xml:coverage.xml --junitxml=test-results.xml tests/
  ```
- **Rule Verification**: All 22 tests pass across roles, auth, duplicate prevention, and health endpoints.
- *Quality Gate Principle*: If any test fails, the pipeline immediately stops in RED with `ABORTED/FAILED` status, preventing bad code from being packaged or deployed.

### Step 6: Docker Image Build
- **Stage 5 (Docker Build)**: Jenkins builds the production Docker container:
  ```bash
  docker build -t placement-management-web:v${BUILD_NUMBER} -t placement-management-web:latest .
  ```
- Container encapsulates Python 3.11-slim, Gunicorn WSGI server, and non-root security user `appuser`.

### Step 7: Push Image to Docker Hub
- **Stage 6 (Docker Hub Push)**: Jenkins authenticates with Docker Hub using securely stored credentials (`dockerhub-creds`):
  ```bash
  docker push <your-dockerhub-username>/placement-management-web:v${BUILD_NUMBER}
  docker push <your-dockerhub-username>/placement-management-web:latest
  ```
- Verify the new tag appears publicly on Docker Hub.

### Step 8: Automated Container Deployment
- **Stage 7 (Deploy)**: Jenkins deploys or rolling-updates the services via Docker Compose:
  ```bash
  docker compose up -d --build
  ```
- Starts containers:
  - `placement_web` (Port 5000)
  - `placement_prometheus` (Port 9090)
  - `placement_grafana` (Port 3000)
  - `placement_node_exporter` (Port 9100)

### Step 9: Automated Smoke Testing
- **Stage 8 (Smoke Test)**: Validates runtime availability before marking the build successful:
  - Performs `curl http://localhost:5000/health` ensuring HTTP 200 and `{"status": "ok"}`.
  - Queries `curl http://localhost:5000/metrics` verifying business telemetry (`placement_registered_students_total`) is present.
- Pipeline marks **Finished: SUCCESS** in bright green!

### Step 10: Verify Running Application & Generate Traffic
1. Open web browser to `http://localhost:5000`.
2. Observe your deployed code change live on the web interface.
3. Run the automated traffic generator script in a separate terminal:
   ```bash
   python scripts/traffic_generator.py --rate 10 --duration 60
   ```
   This simulates realistic student logins, recruiter job reviews, applications, and HTTP traffic.

### Step 11: Real-time Observability in Prometheus & Grafana
1. **Prometheus Targets**:
   - Open `http://localhost:9090/targets`.
   - Confirm both `placement_app` (`web:5000`) and `node_exporter` (`node-exporter:9100`) show state **UP (1/1)** in green.
2. **Grafana Dashboards**:
   - Open `http://localhost:3000` (User: `admin`, Password: `admin`).
   - Navigate to **Dashboards -> Placement Management System - DevOps & Business Analytics**.
   - Watch live charts update every 5 seconds:
     - Application Availability (UP)
     - Host CPU Usage %, Memory Usage %, Disk %, Network I/O
     - Requests per Second & Status Code breakdown
     - Avg & p95 Response Latency
     - Registered Students, Active Jobs, and Application Funnel

### Step 12: Trigger Alerts and Demonstrate Alerting Engine
Simulate real-world failure scenarios and show Prometheus and Grafana alerts firing:

#### Scenario A: Trigger Application Down Alert (`up == 0`)
1. Stop the application container:
   ```bash
   docker stop placement_web
   ```
2. Navigate to `http://localhost:9090/alerts`.
3. Within 30–60 seconds, watch the **ApplicationDown** rule transition from **PENDING** to **FIRING (Red)**!
4. Restart the container to demonstrate auto-recovery:
   ```bash
   docker start placement_web
   ```
5. Refresh `http://localhost:9090/alerts` to show the alert automatically resolves to **OK (Green)**.

#### Scenario B: Trigger High CPU Alert (`CPU > 80%`)
1. Launch a temporary CPU stress container:
   ```bash
   docker run --rm -it progrium/stress --cpu 4 --timeout 45s
   ```
   *(Or on Windows, run a simple CPU load script in Python)*:
   ```bash
   python -c "import multiprocessing; [multiprocessing.Process(target=lambda: [x**2 for x in range(10**7)]).start() for _ in range(multiprocessing.cpu_count())]"
   ```
2. Observe the CPU gauge spike to > 80% on Grafana (`http://localhost:3000`).
3. In Prometheus (`http://localhost:9090/alerts`), verify **HighCpuUsage** transitions into **FIRING**.
4. Allow the load to stop and watch the system restore to normal.

---

## Summary of URLs and Ports for Demo
| Component | URL | Credentials |
| :--- | :--- | :--- |
| **Flask Application** | `http://localhost:5000` | `admin@placement.com` / `Admin@123` |
| **Health API** | `http://localhost:5000/health` | Public |
| **Prometheus Metrics** | `http://localhost:5000/metrics` | Public |
| **Prometheus Web UI** | `http://localhost:9090` | None |
| **Prometheus Targets** | `http://localhost:9090/targets` | None |
| **Prometheus Alerts** | `http://localhost:9090/alerts` | None |
| **Grafana Dashboard** | `http://localhost:3000` | `admin` / `admin` |
| **Node Exporter** | `http://localhost:9100/metrics` | Public |
| **Jenkins CI/CD** | `http://localhost:8080` | Initial admin setup |
