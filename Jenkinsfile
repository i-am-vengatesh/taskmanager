pipeline {
    agent { label 'blackkey' }

    environment {
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

        stage('Install Dependencies / Build') {
            agent {
                docker {
                    image 'vengateshbabu1605/taskmanager-ci:latest'
                    label 'blackkey'
                }
            }
            steps {
                sh '''
                    cd backend
                    mkdir -p ../reports

                    # Sanity check installed packages
                    python -c "import fastapi, httpx, pytest, python_multipart; print('Dependencies OK')"

                    # Record installed packages for traceability
                    python -m pip freeze > ../reports/requirements-freeze.txt
                '''
                stash includes: 'reports/requirements-freeze.txt', name: 'freeze-report'
            }
        }

        stage('Archive Artifacts') {
            steps {
                unstash 'freeze-report'
                archiveArtifacts artifacts: 'reports/requirements-freeze.txt'
            }
        }

        stage('Unit Tests (pytest)') {
            agent {
                docker {
                    image 'vengateshbabu1605/taskmanager-ci:latest'
                    label 'blackkey'
                }
            }
            steps {
                sh '''
                    cd backend
                    export PYTHONPATH=$PWD
                    mkdir -p ../reports

                    # Sanity check dependencies before running tests
                    python -c "import fastapi, httpx; print('Deps OK')"

                    # Run tests
                    pytest --maxfail=1 \
                           --junitxml=../reports/pytest-results.xml \
                           --cov=. \
                           --cov-report=xml:../reports/coverage.xml \
                           --cov-report=term

                    # Capture installed packages
                    python -m pip freeze > ../reports/requirements-freeze-tests.txt
                '''
                stash includes: 'reports/**', name: 'test-reports'
            }
            post {
                always {
                    unstash 'test-reports'
                    archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                    junit testResults: 'reports/pytest-results.xml'
                }
            }
        }

    } // end stages

    post {
        success { echo "Pipeline completed successfully." }
        unstable { echo "Pipeline finished unstable — check test results and reports." }
        failure { echo "Pipeline failed — check console output." }
    }
}
