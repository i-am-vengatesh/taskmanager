pipeline {
    agent { label 'blackkey' }

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

        stage('Unit Tests (pytest)') {
            agent {
                docker {
                    image 'vengateshbabu1605/taskmanager-ci:latest'
                    label 'blackkey'
                    // optional: mount workspace cache if needed
                    // args '-v ${WORKSPACE}/.cache:/root/.cache'
                }
            }
            steps {
                sh '''
                    # Move to backend folder
                    cd backend
                    export PYTHONPATH=$PWD

                    # Ensure reports folder exists
                    mkdir -p ../reports

                    # Run tests
                    pytest --maxfail=1 \
                           --junitxml=../reports/pytest-results.xml \
                           --cov=. \
                           --cov-report=xml:../reports/coverage.xml \
                           --cov-report=term

                    # Save installed packages for traceability
                    python -m pip freeze > ../reports/requirements-freeze-tests.txt
                '''
                // stash test reports for post actions
                stash includes: 'reports/**', name: 'test-reports', allowEmpty: true
            }
            post {
                always {
                    // unstash and archive artifacts
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        unstash 'test-reports'
                    }
                    archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                    junit testResults: 'reports/pytest-results.xml'
                }
                failure {
                    echo "Unit tests failed — check console output and reports."
                }
            }
        }
    }

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
