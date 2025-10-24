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

    stage('Install Dependencies / Build (docker)') {
      agent {
        docker { image 'python:3.11-slim' }
      }
      steps {
        sh '''
          set -e
          cd backend
          python -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt

          mkdir -p ../reports
          pip freeze > ../reports/requirements-freeze.txt
        '''
        // Stash the file so it can be accessed outside the container
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
        docker { image 'python:3.11-slim' }
      }

      steps {
        // make sure we fail fast on any command error
        sh '''
          set -euo pipefail

          # Go to backend where tests and requirements live
          cd backend

          # Create/activate a venv inside the container (keeps deps isolated)
          python -m venv .venv
          . .venv/bin/activate

          # Upgrade pip and install runtime + test deps
          pip install --upgrade pip
          pip install -r requirements.txt || true
          # Ensure testing libs present (safe to install even if already in requirements)
          pip install pytest pytest-mock pytest-cov

          # Ensure workspace reports dir exists on the host workspace
          mkdir -p ../reports

          # Run pytest: produce junit XML and coverage XML outputs
          pytest -q --maxfail=1 \
            --junitxml=../reports/pytest-results.xml \
            --cov=./ \
            --cov-report=xml:../reports/coverage.xml \
            --cov-report=term

          # Save list of installed packages for debugging if needed
          pip freeze > ../reports/requirements-freeze-tests.txt
        '''
        // stash results so later stages or archive step can access them outside the container
        stash includes: 'reports/**', name: 'test-reports'
      }

      post {
        always {
          // Unstash and archive test artifacts for this stage
          catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            unstash 'test-reports'
          }
          archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

          // Publish JUnit results if present (won't fail the pipeline if missing)
          junit testResults: 'reports/pytest-results.xml', allowEmptyResults: true
        }
        failure {
          echo "Unit tests failed — see reports/pytest-results.xml and console log for details."
        }
      }
    } // end Unit Tests stage

  } // end stages

  post {
    failure {
      echo "Pipeline failed — check the console output for errors."
    }
    success {
      echo "Pipeline completed successfully."
    }
  }
}
