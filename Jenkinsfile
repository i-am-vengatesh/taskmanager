pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        // use HTTPS clone with credentials id 'git-creds'
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
      cd backend
      python -m venv .venv
      . .venv/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt
      # Create reports directory in workspace root
      mkdir -p reports
      pip freeze > reports/requirements-freeze.txt

        # Quick smoke test
        python -c "import fastapi; print('fastapi OK', fastapi.__version__)"
    '''
  }
}
    
  }

  post {
    always {
      archiveArtifacts artifacts: 'backend/reports/requirements-freeze.txt', allowEmptyArchive: true
    }
    failure {
      echo "Dependency install or build failed — check pip output above."
    }
  }
}
