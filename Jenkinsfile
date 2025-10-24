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

          # Create & activate venv (optional since image may already have pip/py)
          python -m venv .venv
          . .venv/bin/activate

          # Install only test dependencies (faster)
          python -m pip install --upgrade pip setuptools wheel --no-cache-dir
          python -m pip install --no-cache-dir pytest pytest-mock pytest-cov

          # Run tests (tests import from logic.py, not app.py)
          pytest --maxfail=1 \
                 --junitxml=../reports/pytest-results.xml \
                 --cov=. \
                 --cov-report=xml:../reports/coverage.xml \
                 --cov-report=term

          python -m pip freeze > ../reports/requirements-freeze-tests.txt || true
        '''
        stash includes: 'reports/**', name: 'test-reports', allowEmpty: true
      }
      post {
        always {
          catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            unstash 'test-reports'
          }
          archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
          script {
            if (fileExists('reports/pytest-results.xml')) {
              junit testResults: 'reports/pytest-results.xml', allowEmptyResults: false
            } else {
              error('No test results found (reports/pytest-results.xml). Failing the build.')
            }
          }
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
