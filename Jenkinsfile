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

    stage('Prepare wheelhouse (optional)') {
      when {
        expression { return fileExists("${env.WORKSPACE}/wheelhouse") == false }
      }
      agent {
        docker { image 'python:3.11-slim' }
      }
      steps {
        sh '''
          # This stage only runs when wheelhouse not present. If you do offline builds,
          # you may skip running this on Jenkins and pre-populate wheelhouse manually.
          mkdir -p "${WORKSPACE}/wheelhouse"
          python -m venv .venv
          . .venv/bin/activate
          python -m pip install --upgrade pip setuptools wheel
          python -m pip download --dest "${WORKSPACE}/wheelhouse" -r backend/requirements.txt || true
          ls -la "${WORKSPACE}/wheelhouse" || true
        '''
      }
    }

    stage('Install Dependencies / Build (docker)') {
      agent {
        docker {
          image 'python:3.11-slim'
          args "-v ${WORKSPACE}/.cache:/root/.cache -v ${WORKSPACE}/wheelhouse:/wheelhouse"
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
          python -m pip install --upgrade pip setuptools wheel --no-cache-dir

          # Prefer wheelhouse (offline). If empty or not applicable, fallback to network.
          if [ -d /wheelhouse ] && [ "$(ls -A /wheelhouse 2>/dev/null || true)" != "" ]; then
            echo "Installing from wheelhouse"
            python -m pip install --no-index --find-links=/wheelhouse -r requirements.txt
          else
            echo "Wheelhouse empty or missing — installing from PyPI (network required)"
            python -m pip install --no-cache-dir -r requirements.txt
          fi

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
          args "-v ${WORKSPACE}/wheelhouse:/wheelhouse -v ${WORKSPACE}/.cache:/root/.cache"
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

          python -m venv .venv
          . .venv/bin/activate
          python -m pip install --upgrade pip setuptools wheel --no-cache-dir

          # Install from wheelhouse when available, fallback to network
          if [ -d /wheelhouse ] && [ "$(ls -A /wheelhouse 2>/dev/null || true)" != "" ]; then
            echo "Installing test deps from wheelhouse"
            python -m pip install --no-index --find-links=/wheelhouse -r requirements.txt
          else
            echo "Installing test deps from PyPI (network required)"
            python -m pip install --no-cache-dir -r requirements.txt
          fi

          mkdir -p ../reports

          # Run pytest (if tests fail, keep reports if created)
          pytest --maxfail=1 \
                --junitxml=../reports/pytest-results.xml \
                --cov=. \
                --cov-report=xml:../reports/coverage.xml \
                --cov-report=term || true

          python -m pip freeze > ../reports/requirements-freeze-tests.txt || true
        '''
        // stash even if empty; post will handle missing artifacts gracefully
        stash includes: 'reports/**', name: 'test-reports', allowEmpty: true
      }

      post {
        always {
          // unstash safely: catchError prevents failing if stash missing
          catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            unstash 'test-reports'
          }
          archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
          // require test xml; junit will error if missing and mark build unstable/failing
          junit testResults: 'reports/pytest-results.xml', allowEmptyResults: false
        }
        failure {
          echo "Unit tests stage failed; check console log."
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
