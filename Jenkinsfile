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
  }
}
