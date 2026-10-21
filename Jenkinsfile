pipeline {
    agent any

    triggers {
        // Poll SCM every 2 minutes for automated CI triggers
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE_NAME = 'placement-management-web'
        VENV_DIR = '.venv'
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        ansiColor('xterm')
    }

    stages {
        stage('Checkout') {
            steps {
                echo '===> Stage 1: Checking out repository code...'
                checkout scm
            }
        }

        stage('Setup Virtualenv & Install Dependencies') {
            steps {
                echo '===> Stage 2: Initializing Python virtualenv and installing dependencies...'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint (flake8)') {
            steps {
                echo '===> Stage 3: Running flake8 code quality and style checks...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 app tests config.py run.py seed.py
                '''
            }
        }

        stage('Run Pytest & Coverage') {
            steps {
                echo '===> Stage 4: Executing pytest test suite and generating coverage...'
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

        stage('Build Docker Image') {
            steps {
                echo "===> Stage 5: Building container image tagged as ${BUILD_NUMBER} and latest..."
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Deploy Services') {
            steps {
                echo '===> Stage 6: Deploying web, prometheus, and grafana via Docker Compose...'
                sh '''
                    docker compose up -d --build web prometheus grafana
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                echo '===> Stage 7: Performing smoke test verification on /health and /metrics...'
                sh '''
                    # Wait for container startup and healthcheck readiness
                    echo "Waiting for services to become available..."
                    for i in $(seq 1 12); do
                        if curl -s -f http://localhost:5000/health > /dev/null; then
                            echo "Health check succeeded!"
                            break
                        fi
                        echo "Waiting for service... (attempt $i/12)"
                        sleep 5
                    done

                    # Validate /health endpoint
                    HEALTH_STATUS=$(curl -s http://localhost:5000/health | grep -o '"status": *"ok"')
                    if [ -z "$HEALTH_STATUS" ]; then
                        echo "ERROR: /health response invalid!"
                        exit 1
                    fi
                    echo "Smoke Test Passed: /health returned $HEALTH_STATUS"

                    # Validate /metrics endpoint
                    curl -s -f http://localhost:5000/metrics | grep "placement_registered_students_total" > /dev/null
                    if [ $? -ne 0 ]; then
                        echo "ERROR: Custom business metrics missing from /metrics!"
                        exit 1
                    fi
                    echo "Smoke Test Passed: /metrics returned valid Prometheus telemetry"
                '''
            }
        }
    }

    post {
        always {
            echo '===> Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo '=================================================='
            echo '  CI/CD PIPELINE SUCCEEDED: Build & Deploy Complete'
            echo '=================================================='
        }
        failure {
            echo '=================================================='
            echo '  CI/CD PIPELINE FAILED: Please check stage logs'
            echo '=================================================='
        }
    }
}
