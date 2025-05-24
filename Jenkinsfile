pipeline {
    agent any
    
    options {
        // Remove .git from project URL to test the WebHook
        githubProjectProperty(
            projectUrlStr: 'https://github.com/sfn02/devsecops-demo',
            displayName: 'DevSecOps Pipeline'
        )
        disableConcurrentBuilds()
    }
    
    triggers { 
        githubPush() 
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [
                        [$class: 'CleanBeforeCheckout']
                    ],
                    userRemoteConfigs: [[
                        url: 'https://github.com/sfn02/devsecops-demo.git',
                        credentialsId: 'github_user_pass_token'
                    ]]
                ])
            }
        }

    stage('Unit tests'){
		environment{
			DJANGO_SETTINGS_MODULE='RendezVous.settings.dev'
			}
		steps{withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
			sh '''
			cp $ENV_FILE .env
			python3 -m venv test_env
			. ./test_env/bin/activate
			pip3 install -r requirements-dev.txt
			pytest
            deactivate
			rm -rf ./test_env
			'''
				}
			}
		}
        stage('Build & Integration tests') {

            steps {

                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                    sh '''
                        cp $ENV_FILE .env
                        echo $DOCKER_HOST
                        docker compose up 
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}