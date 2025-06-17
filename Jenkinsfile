pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'pantech-web'
        DOCKER_TAG = 'latest'
    }

    stages {
        stage('Checkout limpio') {
            steps {
                deleteDir()
                checkout scm
            }
        }

        stage('Debug workspace') {
            steps {
                sh 'pwd && echo "Contenido:" && ls -l && echo "Dockerfile:" && cat Dockerfile'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose down --volumes --remove-orphans || true
                    docker volume rm $(docker volume ls -q | grep postgres_data) || true
                    docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                    docker builder prune -af || true
                    docker compose build --no-cache
                    docker compose up -d
                '''
            }
        }
    }

    post {
        failure {
            sh '''
                docker compose logs web || true
                docker compose logs db || true
            '''
        }
        always {
            cleanWs()
        }
    }
}