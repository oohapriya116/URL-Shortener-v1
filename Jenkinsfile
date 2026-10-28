
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies and Test') {
            steps {
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t url-shortener:v1 .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat '''
                        @echo off
                        echo %DH_TOKEN% | docker login -u %DH_USER% --password-stdin
                        if errorlevel 1 exit /b 1
                        docker tag url-shortener:v1 %DH_USER%/url-shortener:v1
                        docker push %DH_USER%/url-shortener:v1
                        docker logout
                    '''
                }
            }
        }
    }
}
