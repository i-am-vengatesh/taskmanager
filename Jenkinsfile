pipeline {
  agent {label 'blackkey'}
  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/i-am-vengatesh/taskmanager.git', credentialsId: 'git-creds'
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
  }

  post {
    failure {
      echo "Dependency install or build failed — check pip output above."
    }
  }
}
