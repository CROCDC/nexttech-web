pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'pantech-web'
        DOCKER_TAG = 'latest'
    }

    stages {
        stage('Deploy') {
            steps {
                sh '''
                    docker compose down || true
                    docker compose up -d --build
                   '''
            }
        }
    }

    post {
        failure {
            sh '''
                docker compose logs web
                docker compose logs db
               '''
        }
        always {
            cleanWs()
        }
    }
}