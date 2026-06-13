pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/ShravaniAWanjari/Brn-tmr-distributed-deployment-workflow.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t brain-tumor-api ./backend'
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
                sh 'curl http://localhost:8000/health'
            }
        }
    }
}