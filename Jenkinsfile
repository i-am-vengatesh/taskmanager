pipeline {
    agent { label 'blackkey' }

    environment {
        // Disable pip version check to reduce network calls
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/i-am-vengatesh/taskmanager.git',
                    credentialsId: 'git-creds'
            }
        }

        stage('Echo') {
            steps {
                sh 'echo "Checkout successful: $(pwd)"; ls -la'
            }
        }

        stage('Prepare Wheelhouse (Optional)') {
            // Only needed first time to pre-download all dependencies into workspace
            agent {
                docker {
                    image 'python:3.11-slim'
                    label 'blackkey'
                }
            }
            steps {
                sh '''
                    mkdir -p "${WORKSPACE}/wheelhouse"
                    python -m venv .venv
                    . .venv/bin/activate

                    # Upgrade pip and build wheelhouse
                    python -m pip install --upgrade pip setuptools wheel
                    python -m pip download --dest "${WORKSPACE}/wheelhouse" -r backend/requirements.txt
                '''
            }
        }

        stage('Install Dependencies / Build (docker)') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    label 'blackkey'
                    args '-v ${WORKSPACE}/.cache:/root/.cache -v ${WORKSPACE}/wheelhouse:/wheelhouse'
                }
            }
            steps {
                sh '''
                    set -euo pipefail

                    mkdir -p "${WORKSPACE}/.cache/pip"
                    export PIP_CACHE_DIR="${WORKSPACE}/.cache/pip"

                    cd backend
                    python -m venv .venv
                    . .venv/bin/activate

                    # Install all dependencies from local wheelhouse (offline)
                    python -m pip install --no-index --find-links=/wheelhouse -r requirements.txt

                    # Record installed packages for traceability
                    mkdir -p ../reports
                    python -m pip freeze > ../reports/requirements-freeze.txt
                '''
                stash includes: 'reports/requirements-freeze.txt', name: 'freeze-report', allowEmpty: true
            }
        }

        stage('Archive Artifacts') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    unstash 'freeze-report'
                }
                archiveArtifacts artifacts: 'reports/requirements-freeze.txt', allowEmptyArchive: true
            }
        }

        stage('Unit Tests (pytest)') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    label 'blackkey'
                    args '-v ${WORKSPACE}/wheelhouse:/wheelhouse'
                }
            }
            steps {
                sh '''
                    set -euo pipefail

                    mkdir -p "${WORKSPACE}/.cache/pip"
                    export PIP_CACHE_DIR="${WORKSPACE}/.cache/pip"
                    export PIP_DISABLE_PIP_VERSION_CHECK=1

                    cd backend
                    export PYTHONPATH=$PWD

                    # Create virtualenv and install dependencies from wheelhouse
                    python -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --no-index --find-links=/wheelhouse -r requirements.txt

                    # Ensure reports directory exists
                    mkdir -p ../reports

                    # Run pytest with coverage
                    pytest --maxfail=1 \
                           --junitxml=../reports/pytest-results.xml \
                           --cov=. \
                           --cov-report=xml:../reports/coverage.xml \
                           --cov-report=term

                    # Freeze installed packages for debugging
                    python -m pip freeze > ../reports/requirements-freeze-tests.txt
                '''
                stash includes: 'reports/**', name: 'test-reports', allowEmpty: true
            }
            post {
                always {
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        unstash 'test-reports'
                    }
                    archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                    junit testResults: 'reports/pytest-results.xml', allowEmptyResults: false
                }
            }
        } // end Unit Tests stage
    } // end stages

    post {
        success {
            echo "Pipeline completed successfully."
        }
        unstable {
            echo "Pipeline finished unstable — check test results and reports."
        }
        failure {
            echo "Pipeline failed — check console output."
        }
    }
}
