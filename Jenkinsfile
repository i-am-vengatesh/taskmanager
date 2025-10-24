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

          # Ensure virtualenv exists
          python -m venv .venv
          . .venv/bin/activate

          # Upgrade pip and install all requirements
          python -m pip install --upgrade pip setuptools wheel --no-cache-dir
          python -m pip install --no-cache-dir -r requirements.txt

          # Create reports folder and record installed packages
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
        }
      }
      steps {
        sh '''
          cd backend

          # Ensure PYTHONPATH points to backend folder
          export PYTHONPATH=$PWD

          # Activate virtualenv
          . .venv/bin/activate

          # Ensure reports directory exists
          mkdir -p ../reports

          # Run pytest explicitly on tests folder
          pytest tests/ \
              --maxfail=1 \
              --junitxml=../reports/pytest-results.xml \
              --cov=. \
              --cov-report=xml:../reports/coverage.xml \
              --cov-report=term

          # Record installed packages after test run
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
        failure {
          echo "Unit tests stage failed; check console output and reports/ for details."
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
