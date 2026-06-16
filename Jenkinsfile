pipeline {
    agent {
        label 'docker-agent'
    }

    environment {
        IMAGE_NAME = '22jadex/brain-tumor-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t brain-tumor-api ./backend'
            }
        }

        stage('Verify Image') {
            steps {
                sh 'docker images | grep brain-tumor-api'
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'a755cfbd-afee-48e6-b49a-b38616cb5e05',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    '''
                }
            }
        }
        stage('Push To Docker Hub') {
            steps {
                sh '''
                docker tag brain-tumor-api 22jadex/brain-tumor-api:${BUILD_NUMBER}
                docker tag brain-tumor-api 22jadex/brain-tumor-api:latest

                docker push 22jadex/brain-tumor-api:${BUILD_NUMBER}
                docker push 22jadex/brain-tumor-api:latest
                '''
            }
        }

        stage('Deploy With Ansible') {
            steps {
                sh '''
                cd infra/ansible
                ansible-playbook -i inventory.ini deploy.yml
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh 'curl http://host.docker.internal:8000/health'
            }
        }
    }
}