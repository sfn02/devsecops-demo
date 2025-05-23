pipeline {
    agent any
    options {
        githubProjectProperty(projectUrlStr: 'https://github.com/sfn02/devsecops-demo.git')
    

        disableConcurrentBuilds() 
    }
    triggers { githubPush() }


    stages {
        stage('Checkout code') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], 
                extensions: [], 
                userRemoteConfigs: [[credentialsId: 'github_user_pass_token', 
                url: 'https://github.com/sfn02/devsecops-demo.git']])

        }

        stage('Run unit tests'){
            environment{
                DJANGO_SETTINGS_MODULE='RendezVous.settings.dev'
            }

            steps{
            withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                sh '''
                    ls
                    '''
                }

            }

        }
//
        stage('Build'){
    steps{
        withCredentials([file(credentialsId: 'env_file_prod', variable: 'ENV_FILE')]) {
            sh '''
            pwd
            '''
        }
    }
}

    }
} 
