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
                    docker compose down --remove-orphans || true
                    docker rmi pantech-web:latest || true
                    docker compose build --no-cache
                    docker compose up -d
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