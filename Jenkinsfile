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