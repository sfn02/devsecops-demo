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
                userRemoteConfigs: [[url: 'https://github.com/sfn02/devsecops-demo.git']])
            }

        }

        stage('Run unit tests'){
            environment{
                DJANGO_SETTINGS_MODULE='RendezVous.settings.dev'
            }

            steps{
            withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                sh '''

                python3 -m venv test_env

                . ./test_env/bin/activate

                cp $ENV_FILE .env

                chmod 600 .env  
                python -m pip install --upgrade pip
                python -m pip install python-dotenv
                python -c 'from dotenv import load_dotenv;import os;load_dotenv();x = os.environ["DEBUG"];print(x)'
                cat .env
                echo $ALLOWED_HOSTS
                deactivate
                rm -rf ./test_env
                    '''

                }

            }

        }

        stage('Build'){
    steps{
        withCredentials([file(credentialsId: 'env_file_prod', variable: 'ENV_FILE')]) {
            sh '''
            python3 -m venv prod_env
            . ./prod_env/bin/activate
            cp $ENV_FILE .env
            chmod 600 .env 
            export $(grep -v '^#' .env | grep '^DJANGO_SETTINGS_MODULE' |xargs) 
            ls nginx.d
            pwd 

            echo "Starting Docker Compose services..."
            docker-compose up nginx # Run in detached mode so pipeline can run other commands
            
            echo "Giving services some time to start up..."
            sleep 15 # Give the app and nginx a moment to initialize
            
            echo "Checking status of Docker containers:"
            docker-compose ps -a # Show all containers, including exited ones
            echo "Displaying Nginx container logs for debugging:"
            docker-compose logs nginx # Get logs specifically from the Nginx container       
            echo "Displaying Web container logs for debugging:"
            docker-compose logs web # Get logs specifically from the Django web container
            echo "Attempting to access Nginx from Jenkins agent host:"
            echo "Bringing down Docker Compose services..."
            '''
        }
    }
}

    }
} 
