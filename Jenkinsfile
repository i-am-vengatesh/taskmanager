pipeline {
  agent { label 'blackkey' }

  environment {
    // disable pip version check to reduce network calls
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

    stage('Install Dependencies / Build (docker)') {
      agent {
        
        docker {
          image 'python:3.11-slim'
          label 'blackkey'
          // optional args: pass proxy env vars or mount cache if needed
          // args '-e HTTP_PROXY=$HTTP_PROXY -e HTTPS_PROXY=$HTTPS_PROXY -v ${WORKSPACE}/.cache:/root/.cache'
        }
        
      }
      steps {
        sh '''
          set -euo pipefail

          # Ensure workspace pip cache dir exists and is writable
          mkdir -p "${WORKSPACE}/.cache/pip"
          export PIP_CACHE_DIR="${WORKSPACE}/.cache/pip"

          cd backend

          # Create virtualenv and activate
          python -m venv .venv
          . .venv/bin/activate

          # Use python -m pip to avoid ambiguity and avoid writing to root cache
          python -m pip install --upgrade pip setuptools wheel --no-cache-dir || true

          # Install runtime dependencies; if network is unavailable, allow failure for now (remove || true later)
          python -m pip install --no-cache-dir -r requirements.txt || true

          # Record installed packages for traceability
          mkdir -p ../reports
          python -m pip freeze > ../reports/requirements-freeze.txt || true
        '''
        // stash the freeze so other stages can access it
        stash includes: 'reports/requirements-freeze.txt', name: 'freeze-report', allowEmpty: true
      }
    }

    stage('Archive Artifacts') {
      steps {
        // restore freeze report and archive it
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          unstash 'freeze-report'
        }
        archiveArtifacts artifacts: 'reports/requirements-freeze.txt', allowEmptyArchive: true
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
            export PIP_DISABLE_PIP_VERSION_CHECK=1

            cd backend
            export PYTHONPATH=$PWD
            python -m venv .venv || true
            . .venv/bin/activate || true

            python -m pip install --no-cache-dir pytest pytest-mock pytest-cov || true
            mkdir -p ../reports

            # Run tests
            pytest --maxfail=1 \
                --junitxml=../reports/pytest-results.xml \
                --cov=. \
                --cov-report=xml:../reports/coverage.xml \
                --cov-report=term || true

            # Fail if no tests ran
            if [ ! -s ../reports/pytest-results.xml ]; then
                echo "ERROR: No tests were found! Failing the build."
                exit 1
            fi

            python -m pip freeze > ../reports/requirements-freeze-tests.txt || true
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
        failure {
            echo "Unit tests stage failed; check console output and reports/ for details."
        }
    }
}
 // end Unit Tests stage

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
