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

        stage('Install / Build') {
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

                    # Sanity check: ensure dependencies exist
                    python -c "import fastapi, httpx; print('Deps OK')"

                    # Run tests
                    pytest --maxfail=1 \
                           --junitxml=../reports/pytest-results.xml \
                           --cov=. \
                           --cov-report=xml:../reports/coverage.xml \
                           --cov-report=term

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
    }

    post {
        success { echo "Pipeline completed successfully." }
        unstable { echo "Pipeline finished unstable — check test results and reports." }
        failure { echo "Pipeline failed — check console output." }
    }
}
