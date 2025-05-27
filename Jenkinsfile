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
    environment {
        LOGDIR="/security/logs/build-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Preparing Log directory'){
            steps{
                sh 'mkdir -p ${LOGDIR}'
            }
        }
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

        stage('SAST'){
            parallel{
                stage('SAST semgrep'){
                    steps{
                        script{
                            sh 'semgrep scan  --json --exclude "static/" --exclude "tests/" --severity "WARNING" > semgrep_scan.json || true'
                            def warningsCount = sh(
                                script: 'jq -r \'[.results[].extra | select(.severity == \"WARNING\")] | length\' semgrep_scan.json',
                                returnStdout: true
                                ).trim().toInteger()
                                sh """jq -c '.results[] | {pipeline_job: env.JOB_NAME,
                                        build_number: env.BUILD_NUMBER,
                                        check_id: .check_id,
                                        path: .path,
                                        severity: .extra.severity,
                                        message: .extra.message,
                                        owasp: .extra.metadata.owasp,
                                        cwe: .extra.metadata.cwe}' semgrep_scan.json 
                                        > ${LOGDIR}/semgrep.log"""
                                if (warningsCount > 0){
                                    error "${warningsCount} Critical vulnerabilities found"
                                }
                                else{
                                    echo "Quality gates passed"
                            }
                        }

                    }
                }
        stage('SAST Bandit') {
            steps {
                script {
                    sh """
                        bandit -r . -f json --exclude "static/" > bandit_scan.json || true
                        """

                    def highSeverityCount = sh(
                        script: 'jq -r \'[.results[] | select(.issue_severity == "HIGH")] | length\' bandit_scan.json',
                        returnStdout: true
                        ).trim().toInteger()

                    def mediumSeverityCount = sh(
                        script: 'jq -r \'[.results[] | select(.issue_severity == "MEDIUM")] | length\' bandit_scan.json',
                        returnStdout: true
                        ).trim().toInteger()

                    echo "Bandit Scan Summary: ${highSeverityCount} HIGH severity findings, ${mediumSeverityCount} MEDIUM severity findings."

                    if (highSeverityCount > 0 || mediumSeverityCount > 0) {
                        sh """
                            jq -c '
                            .results[] | {
                            tool: "bandit",
                            pipeline_job: "${env.JOB_NAME}",
                            build_number: "${env.BUILD_NUMBER}",
                            filename: .filename,          
                            line_number: .line_number,   
                            severity: .issue_severity,   
                            confidence: .issue_confidence,
                            test_id: .test_id,           
                            message: .issue_text,        
                            more_info: .more_info        
                            }'
                            bandit_scan.json > "${LOGDIR}/bandit.log"
                        """
                        echo "Detailed Bandit findings logged to ${LOGDIR}/bandit.log"
                    }
                    else {
                        echo "No Bandit findings (HIGH, MEDIUM) to log in detail."
                    }
                }
            }

        }
    }
}
}

        stage('Unit tests'){
	   	   environment{
	   		  DJANGO_SETTINGS_MODULE='RendezVous.settings.dev'
	   		}
	   	   steps{
                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
	   		          sh '''
	   		          cp $ENV_FILE .env
	   		          python3 -m venv test_env
	   		          . ./test_env/bin/activate
	   		          pip3 install -r requirements-dev.txt
	   		          python -m pytest > ${LOGDIR}/pytest.log
                      deactivate
	   		          rm -rf ./test_env 
	   		      '''
	   			}
	   		}
	   	}

        stage('Build & Integration tests') {
            steps {
                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                    sh """
                        cp $ENV_FILE .env
                        docker compose -f docker-compose.dev.yaml up -d
                        newman run tests/collection.json \
                        -e tests/environment.json --env-var "BaseUrl=http://rendez-vous.test" \
                        --env-var "skip_registration=false" 2>&1 1>${LOGDIR}/newman.log
                    """
                    }
                }
            }
        }
    
    post {
        always {
            archiveArtifacts artifacts: 'semgrep_scan.json, bandit_scan.json', allowEmpty: true
            cleanWs()
        }
    }
}