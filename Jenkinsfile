pipeline {
  agent { label 'blackkey' }

  environment {
    // avoids pip version-check network calls if pip is invoked elsewhere
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
          // prebuilt image with all runtime & test deps baked in
          image 'vengateshbabu1605/taskmanager-ci:latest'
          label 'blackkey'
        }
      }
      steps {
        sh '''
          set -euo pipefail
          cd backend
          mkdir -p ../reports
          # Capture the environment packages inside the prebuilt image (for traceability)
          python -m pip freeze > ../reports/requirements-freeze.txt || true
        '''
        // stash freeze but allow empty (safe during iteration)
        stash includes: 'reports/requirements-freeze.txt', name: 'freeze-report', allowEmpty: true
      }
    }

    stage('Archive Artifacts') {
      steps {
        // unstash safely
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

          # Work from backend folder so imports resolve (tests import logic module)
          cd backend
          export PYTHONPATH=$PWD
          mkdir -p ../reports

          # Ensure pytest is available in the prebuilt image; fail fast with helpful message
          if ! command -v pytest >/dev/null 2>&1; then
            echo "ERROR: pytest not found in image 'vengateshbabu1605/taskmanager-ci:latest'"
            echo "Rebuild the image to include pytest/pytest-cov or switch to a different image."
            exit 2
          fi

          # Run tests (image already contains runtime and test deps)
          pytest --maxfail=1 \
                 --junitxml=../reports/pytest-results.xml \
                 --cov=. \
                 --cov-report=xml:../reports/coverage.xml \
                 --cov-report=term

          # Record installed packages for traceability (non-fatal)
          python -m pip freeze > ../reports/requirements-freeze-tests.txt || true
        '''
        // stash results (allowEmpty to avoid stash errors if something weird happens)
        stash includes: 'reports/**', name: 'test-reports', allowEmpty: true
      }

      post {
        always {
          // Unstash safely; do not throw if stash missing
          catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            unstash 'test-reports'
          }

          // Archive whatever is under reports
          archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

          // Require JUnit XML to exist and contain results; fail stage if missing
          script {
            if (fileExists('reports/pytest-results.xml')) {
              junit testResults: 'reports/pytest-results.xml', allowEmptyResults: false
            } else {
              error('No test results found (reports/pytest-results.xml). Failing the build to avoid false success.')
            }
          }
        }
        failure {
          echo "Unit tests stage failed — check console output and reports for details."
        }
      }
    } // end Unit Tests

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
