pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'pantechsolutions-web'
        DOCKER_TAG = 'latest'
    }

    stage('Checkout limpio') {
        steps {
            deleteDir()
            checkout scm
        }
    }

    stages {
        stage('Deploy') {
            steps {
                sh '''
                    docker compose down --remove-orphans || true
                    docker rmi pantechsolutions-web:latest || true
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