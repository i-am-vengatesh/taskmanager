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
          set -euo pipefail
          cd backend
          mkdir -p ../reports
          python -m pip freeze > ../reports/requirements-freeze.txt || true
        '''
        // stash the freeze; allowEmpty in case something went wrong earlier
        stash includes: 'reports/requirements-freeze.txt', name: 'freeze-report', allowEmpty: true
      }
    }

    stage('Archive Artifacts') {
      steps {
        // unstash safely (won't fail the pipeline if stash is missing)
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          unstash 'freeze-report'
        }
        archiveArtifacts artifacts: 'reports/requirements-freeze.txt', allowEmptyArchive: true
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
          set -euo pipefail
          cd backend
          export PYTHONPATH=$PWD
          mkdir -p ../reports

          # Run tests (image already has dependencies)
          pytest --maxfail=1 \
                 --junitxml=../reports/pytest-results.xml \
                 --cov=. \
                 --cov-report=xml:../reports/coverage.xml \
                 --cov-report=term

          python -m pip freeze > ../reports/requirements-freeze-tests.txt || true
        '''
        // stash test reports; allowEmpty so stash won't fail if something crashed early
        stash includes: 'reports/**', name: 'test-reports', allowEmpty: true
      }

      post {
        always {
          // Unstash safely (catchError prevents "No such stash" exceptions)
          catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            unstash 'test-reports'
          }

          // Archive anything under reports (won't fail if empty)
          archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

          // Require JUnit XML to exist and contain results; fail the stage if missing
          script {
            if (fileExists('reports/pytest-results.xml')) {
              junit testResults: 'reports/pytest-results.xml', allowEmptyResults: false
            } else {
              // No test results means we should fail the build (prevents false success)
              error('No test results found (reports/pytest-results.xml). Failing the build.')
            }
          }
        }
        failure {
          echo "Unit tests stage failed; check console output and reports for details."
        }
      }
    } // end Unit Tests
  } // end stages

  post {
    success { echo "Pipeline completed successfully." }
    unstable { echo "Pipeline finished unstable — check test results and reports." }
    failure { echo "Pipeline failed — check console output." }
  }
}
