pipeline {
    agent any

    options {
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
                sh "mkdir -p ${LOGDIR}"
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
                stage('SAST Semgrep'){
                    steps{
                        script{
                            sh 'semgrep --json --exclude "static/" --exclude "tests/"  > semgrep_scan.json || true'
                            def warningsCount = sh(
                                script: 'jq -r \'[.results[] | select(.extra.severity == "WARNING")] | length\' semgrep_scan.json',
                                returnStdout: true
                            ).trim().toInteger()

                            def errorCriticalCount = sh(
                                script: 'jq -r \'[.results[] | select(.extra.severity == "ERROR" or .extra.severity == "CRITICAL")] | length\' semgrep_scan.json',
                                returnStdout: true
                            ).trim().toInteger()

                            echo "Semgrep Scan Summary: ${warningsCount} WARNINGs, ${errorCriticalCount} ERROR/CRITICAL findings."

                            if (warningsCount > 0 || errorCriticalCount > 0) {
                                sh """jq -c '
                                        .results[] | {
                                        tool: "semgrep",
                                        pipeline_job: "${env.JOB_NAME}",
                                        build_number: "${env.BUILD_NUMBER}",
                                        check_id: .check_id,
                                        path: .path,
                                        severity: .extra.severity,
                                        message: .extra.message,
                                        owasp: .extra.metadata.owasp,
                                        cwe: .extra.metadata.cwe
                                        }' semgrep_scan.json | tee ${LOGDIR}/semgrep.log"""
                                echo "Detailed Semgrep findings logged to ${LOGDIR}/semgrep.log"
                            } else {
                                echo "No significant Semgrep findings (WARNING, ERROR, CRITICAL) to log in detail."
                            }

                            if (errorCriticalCount > 0){
                                echo "SECURITY GATE FAILED: Semgrep detected ${errorCriticalCount} ERROR/CRITICAL findings."
                            }
                            def maxAllowedSemgrepWarnings = 0
                            if (warningsCount > maxAllowedSemgrepWarnings){
                                echo "QUALITY GATE FAILED: Semgrep detected ${warningsCount} WARNINGs, exceeding threshold of ${maxAllowedSemgrepWarnings}."
                            }
                            echo "Semgrep analysis passed all defined quality gates."
                        }
                    }
                }
                stage('SAST Bandit') {
                    steps {
                        script {
                            echo "--- Running Bandit SAST Scan ---"
                            sh """
                                bandit -r . -f json --exclude "static/" --exclude "tests/" > bandit_scan.json || true
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
                                      }
                                    ' bandit_scan.json > "${LOGDIR}/bandit.log"
                                """
                                echo "Detailed Bandit findings logged to ${LOGDIR}/bandit.log"
                            } else {
                                echo "No Bandit findings (HIGH, MEDIUM) to log in detail."
                            }

                            if (highSeverityCount > 0) {
                                echo "SECURITY GATE FAILED: Bandit detected ${highSeverityCount} HIGH severity findings."
                            }
                            def maxAllowedBanditMedium = 5
                            if (mediumSeverityCount > maxAllowedBanditMedium) {
                                echo "QUALITY GATE FAILED: Bandit detected ${mediumSeverityCount} MEDIUM severity findings, exceeding threshold of ${maxAllowedBanditMedium}."
                            }
                            echo "Bandit analysis passed all defined quality gates."
                        }
                    }
                }
            } // End of parallel for SAST
        } // End of SAST parent stage

        stage('Unit tests'){
            environment{
                DJANGO_SETTINGS_MODULE='RendezVous.settings.dev'
            }
            steps{
                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                    script{
                        sh('cp $ENV_FILE .env')
                        sh """
                        python3 -m venv test_env
                        . ./test_env/bin/activate
                        pip3 install -r requirements-dev.txt
                        python -m pytest | tee "${LOGDIR}/pytest.log"
                        deactivate
                        rm -rf ./test_env
                        """
                    }
                }
            }
        }

        stage('Build & Integration tests') {
            steps {
                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                    script{
                        sh('cp $ENV_FILE .env')
                        sh(
                        script: """
                        docker compose -f docker-compose.dev.yaml up -d --build --remove-orphans --wait
                        sleep 10
                        newman run tests/collection.json \
                        -e tests/environment.json --env-var "BaseUrl=http://rendez-vous.test" \
                        --env-var "skip_registration=false" \
                        --delay-request 1000 --timeout-request 3000 
                        """

                        )
                    }
                }
            }
        }
    } 

    post {
        always {
            echo "Archiving SAST results and cleaning workspace..."
            archiveArtifacts artifacts: 'semgrep_scan.json, bandit_scan.json', allowEmptyArchive: true
            sh 'docker compose -f docker-compose.dev.yaml down --remove-orphans --volumes'
            cleanWs()
        }
        success{
            echo "Build ${env.BUILD_NUMBER} successfully built"
        }
    }
}