pipeline {
    agent any

    triggers {
        // Triggered automatically via GitHub webhook push events
        githubPush()
        // Fallback SCM polling every 2 minutes
        pollSCM('H/2 * * * *')
    }

    environment {
        APP_NAME = 'placement-management-web'
        VENV_DIR = '.venv'
        DOCKER_CREDS_ID = 'dockerhub-creds'
    }

    options {
        timeout(time: 25, unit: 'MINUTES')
        ansiColor('xterm')
    }

    stages {
        stage('Checkout') {
            steps {
                echo '===> [Stage 1/8] Checking out repository source code from Git...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '===> [Stage 2/8] Setting up Python virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Build & Lint') {
            steps {
                echo '===> [Stage 3/8] Running code quality and style analysis (flake8)...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 app tests config.py run.py seed.py
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                echo '===> [Stage 4/8] Running pytest test suite (Rule: if tests fail, pipeline stops immediately)...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v --cov=app --cov-report=xml:coverage.xml --cov-report=term --junitxml=test-results.xml tests/
                '''
            }
            post {
                always {
                    junit testResults: 'test-results.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'coverage.xml, test-results.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "===> [Stage 5/8] Building Docker image tagged v${BUILD_NUMBER} and latest..."
                sh '''
                    docker build -t ${APP_NAME}:v${BUILD_NUMBER} -t ${APP_NAME}:latest .
                '''
            }
        }

        stage('Docker Hub Push') {
            steps {
                echo '===> [Stage 6/8] Authenticating and pushing Docker image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker tag ${APP_NAME}:v${BUILD_NUMBER} ${DOCKER_USER}/${APP_NAME}:v${BUILD_NUMBER}
                        docker tag ${APP_NAME}:latest ${DOCKER_USER}/${APP_NAME}:latest
                        docker push ${DOCKER_USER}/${APP_NAME}:v${BUILD_NUMBER}
                        docker push ${DOCKER_USER}/${APP_NAME}:latest
                        echo "Docker Hub push completed successfully: ${DOCKER_USER}/${APP_NAME}:v${BUILD_NUMBER}"
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '===> [Stage 7/8] Deploying application stack via Docker Compose...'
                sh '''
                    docker compose down --remove-orphans || true
                    docker compose up -d --build
                    echo "Application stack deployed successfully via Docker Compose."
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                echo '===> [Stage 8/8] Running automated smoke tests on /health and /metrics...'
                sh '''
                    echo "Waiting for web application container to become healthy..."
                    HEALTHY=0
                    for i in $(seq 1 15); do
                        if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
                            echo "Health check responded successfully on attempt $i!"
                            HEALTHY=1
                            break
                        fi
                        echo "Waiting for container startup... (attempt $i/15)"
                        sleep 4
                    done

                    if [ $HEALTHY -ne 1 ]; then
                        echo "FATAL: /health did not respond within expected startup window!"
                        exit 1
                    fi

                    # Validate /health JSON response payload
                    HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
                    echo "Health API Response: $HEALTH_RESPONSE"
                    if ! echo "$HEALTH_RESPONSE" | grep -q '"status": *"ok"'; then
                        echo "FATAL: /health payload does not contain {\"status\": \"ok\"}!"
                        exit 1
                    fi

                    # Validate /metrics Prometheus telemetry
                    echo "Verifying Prometheus /metrics exposition..."
                    METRICS_OUTPUT=$(curl -s http://localhost:5000/metrics)
                    if ! echo "$METRICS_OUTPUT" | grep -q "placement_registered_students_total"; then
                        echo "FATAL: Custom metrics missing from /metrics endpoint!"
                        exit 1
                    fi
                    echo "Smoke Test Passed: All endpoints responding with valid payloads."
                '''
            }
        }
    }

    post {
        always {
            echo '===> Pipeline execution completed. Cleaning temporary workspace artifacts...'
            cleanWs deleteDirs: true, notFailBuild: true
        }
        success {
            echo '====================================================='
            echo '✓ CI/CD PIPELINE SUCCEEDED: ALL STAGES PASSED CLEANLY'
            echo '====================================================='
        }
        failure {
            echo '====================================================='
            echo '✗ CI/CD PIPELINE FAILED: DEPLOYMENT HALTED OR FAILED'
            echo '====================================================='
        }
    }
}
