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
    docker {
      image 'python:3.11-slim'
      // optional: pass docker args
      // args '--network host -v ${WORKSPACE}/.cache:/root/.cache'
    }
  }
  steps {
    sh '''
      set -euo pipefail

      # create a pip cache inside Jenkins workspace (writable)
      mkdir -p "${WORKSPACE}/.cache/pip"
      export PIP_CACHE_DIR="${WORKSPACE}/.cache/pip"

      cd backend

      python -m venv .venv
      . .venv/bin/activate

      # use python -m pip to avoid ambiguity, set timeout and avoid using pip's in-memory cache
      python -m pip install --upgrade pip
      python -m pip install --no-cache-dir --timeout 60 -r requirements.txt

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
    docker { image 'python:3.11-slim' }
  }
  steps {
    sh '''
      set -euo pipefail

      mkdir -p "${WORKSPACE}/.cache/pip"
      export PIP_CACHE_DIR="${WORKSPACE}/.cache/pip"

      cd backend
      python -m venv .venv
      . .venv/bin/activate

      python -m pip install --upgrade pip
      python -m pip install --no-cache-dir --timeout 60 -r requirements.txt || true
      python -m pip install --no-cache-dir pytest pytest-mock pytest-cov

      mkdir -p ../reports

      pytest -q --maxfail=1 \
        --junitxml=../reports/pytest-results.xml \
        --cov=./ \
        --cov-report=xml:../reports/coverage.xml \
        --cov-report=term

      python -m pip freeze > ../reports/requirements-freeze-tests.txt
    '''
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
