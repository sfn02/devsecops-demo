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
        DEPLOY_ALLOWED = "true" 
    }

    stages {
        stage('Preparing Log directory') {
            steps {
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

        stage('Secrets Scanning') {
            parallel {
                stage('Secrets Scanning - Trivy') {
                    steps {
                        script {
                            sh '/security/trivy/trivy fs --scanners secret --secret-config trivy-secret.yaml \
                            --skip-dirs static,tests,*/migrations \
                            -f json . | tee trivy_scan.json'
                            
                            sh """
                                jq -c '                                                                                                           
                                  .Results[] | .Secrets[] |
                                  {
                                    tool: "trivy",
                                    pipeline_job: "${env.JOB_NAME}",
                                    build_number: "${env.BUILD_NUMBER}",
                                    Path: .Target, 
                                    start_line: .StartLine,  
                                    end_line: .EndLine,
                                    severity: .Severity,
                                    description: .Title,
                                    match: .Match
                                  }' trivy_scan.json | \
                                  tee ${LOGDIR}/trivy_scan.log
                            """
                            
                            def trivyCriticalHighCount = sh(
                                script: 'jq -r \'[.Results[] | .Secrets[] | select(.Severity == "CRITICAL" or .Severity == "HIGH")] | length\' trivy_scan.json',
                                returnStdout: true
                            ).trim().toInteger()

                            if (trivyCriticalHighCount > 0) {
                                echo "SECURITY GATE FAILED: Trivy detected ${trivyCriticalHighCount} Critical/High secrets. Deployment will be blocked."
                                env.DEPLOY_ALLOWED = "false"
                            } else {
                                echo "Trivy secret scan passed security gate."
                            }
                        }
                    }
                }
                stage('Secrets Scanning - Gitleaks') {
                    steps {
                        script {
                            sh 'gitleaks detect . -v -f json -r gitleaks_scan.json'
                            
                            sh """
                                jq -c '
                                    .[] | 
                                  {
                                    tool: "gitleaks",
                                    pipeline_job: "${env.JOB_NAME}",
                                    build_number: "${env.BUILD_NUMBER}", 
                                    Path: .File,           
                                    start_line: .StartLine, 
                                    end_line: .EndLine,     
                                    severity: "UNKNOWN",
                                    description: .Description,
                                    match: .Match      
                                  }' gitleaks_scan.json | tee ${LOGDIR}/gitleaks_scan.log
                            """
                            
                            def gitleaksFindingsCount = sh(
                                script: 'jq -r \'. | length\' gitleaks_scan.json',
                                returnStdout: true
                            ).trim().toInteger()

                            if (gitleaksFindingsCount > 0) {
                                echo "SECURITY GATE FAILED: Gitleaks detected ${gitleaksFindingsCount} secrets. Deployment will be blocked."
                                env.DEPLOY_ALLOWED = "false"
                            } else {
                                echo "Gitleaks scan passed security gate."
                            }
                        }
                    }
                }
            }
        }

        stage('SAST') {
            parallel {
                stage('SAST Semgrep') {
                    steps {
                        script {
                            sh(script: 'semgrep --json --exclude "static/" --exclude "tests/" > semgrep_scan.json', returnStatus: true)
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
                            }

                            if (errorCriticalCount > 0) {
                                echo "SECURITY GATE FAILED: Semgrep detected ${errorCriticalCount} ERROR/CRITICAL findings. Deployment will be blocked."
                                env.DEPLOY_ALLOWED = "false"
                            }
                            def maxAllowedSemgrepWarnings = 0
                            if (warningsCount > maxAllowedSemgrepWarnings) {
                                echo "QUALITY GATE FAILED: Semgrep detected ${warningsCount} WARNINGs, exceeding threshold of ${maxAllowedSemgrepWarnings}. Deployment will be blocked."
                                env.DEPLOY_ALLOWED = "false"
                            }
                            if (env.DEPLOY_ALLOWED == "true") {
                                echo "Semgrep analysis passed all defined quality gates."
                            }
                        }
                    }
                }
                stage('SAST Bandit') {
                    steps {
                        script {
                            sh(script: 'bandit -r . -f json --exclude "static/" --exclude "*/tests/" > bandit_scan.json', returnStatus: true)

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
                                    ' bandit_scan.json | tee ${LOGDIR}/bandit.log
                                """
                                echo "Detailed Bandit findings logged to ${LOGDIR}/bandit.log"
                            }

                            if (highSeverityCount > 0) {
                                echo "SECURITY GATE FAILED: Bandit detected ${highSeverityCount} HIGH severity findings. Deployment will be blocked."
                                env.DEPLOY_ALLOWED = "false"
                            }
                            def maxAllowedBanditMedium = 5
                            if (mediumSeverityCount > maxAllowedBanditMedium) {
                                echo "QUALITY GATE FAILED: Bandit detected ${mediumSeverityCount} MEDIUM severity findings, exceeding threshold of ${maxAllowedBanditMedium}. Deployment will be blocked."
                                env.DEPLOY_ALLOWED = "false"
                            }
                            if (env.DEPLOY_ALLOWED == "true") {
                                echo "Bandit analysis passed all defined quality gates."
                            }
                        }
                    }
                }
            } 
        } 

        stage('Unit tests & SCA') {
            environment {
                DJANGO_SETTINGS_MODULE = 'RendezVous.settings.dev'
            }
            steps {
                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                    script {
                        sh('cp $ENV_FILE .env')
                        sh """
                        python3 -m venv test_env
                        . ./test_env/bin/activate
                        python -m pip install --upgrade pip
                        python -m pip install -r requirements-dev.txt 
                        python -m pip install pip-audit
                        pip-audit -f json --strict > pip_audit_scan.json || true
                        pip-audit -f json --strict --fix 
                        deactivate
                        """

                        def pipAuditCount = sh(
                            script: 'jq \'[.dependencies[] | select(.vulns[] != null)] | length\' pip_audit_scan.json',
                            returnStdout: true
                        ).trim().toInteger()

//trigger 
                        echo "pip-audit Scan Summary: ${pipAuditCount}  findings."

                        if (pipAuditCount > 0 ) {
                            sh """
                                jq -c '
                                .vulnerabilities[] | {
                                tool: "pip-audit",
                                pipeline_job: "${env.JOB_NAME}",
                                build_number: "${env.BUILD_NUMBER}",
                                dependency: .dependency.name,
                                version: .dependency.version,
                                vulnerability_id: .vulns[],
                                description: .description,
                                fix_versions: .fix_versions
                                }' pip_audit_scan.json | tee ${LOGDIR}/pip_audit.log
                            """
                            echo "SECURITY GATE FAILED: pip-audit detected ${pipAuditCount} Critical/High severity findings. Deployment will be blocked."
                            env.DEPLOY_ALLOWED = "false"
                        }
                        
                        sh """
                        . test_env/bin/activate
                        python -m pytest --json-report --json-report-summary --json-report-file ${LOGDIR}/pytest-summary.log &
                        python -m pytest --json-report --json-report-file ./pytest-full-report.json
                        deactivate
                        rm -rf ./test_env
                        """
                    }
                }
            }
        }

        stage('IaC Scanning') {
            steps {
                script {
                    echo 'Running trivy scan against dockerfiles...'
                    sh """
                        /security/trivy/trivy config --severity HIGH,CRITICAL \
                        --file-patterns 'dockerfile:dockerfile' . \
                        -f json > trivy_iac_scan.json || true
                        cat trivy_iac_scan.json | tee ${LOGDIR}/trivy_iac_scan.log
                    """
                    
                    def trivyIacCriticalHighCount = sh(
                        script: """jq -r '[.Results[] | select(.Misconfigurations > 0 ) |\
                            .Misconfigurations[] | select(.Severity == "CRITICAL" or .Severity == "HIGH")] | \
                            length' trivy_iac_scan.json""",
                        returnStdout: true
                    ).trim().toInteger()

                    if (trivyIacCriticalHighCount > 0) {
                        echo "SECURITY GATE FAILED: Trivy IaC scan detected ${trivyIacCriticalHighCount} Critical/High misconfigurations. Deployment will be blocked."
                        env.DEPLOY_ALLOWED = "false"
                    }
                }
            }
        }
        
        stage('Build & Integration tests') {
            steps {
                withCredentials([file(credentialsId: 'env_file_dev', variable: 'ENV_FILE')]) {
                    script {
                        sh('cp $ENV_FILE .env')
                        sh """
                        sudo /setup.sh
                        docker compose -f docker-compose.dev.yaml build --no-cache
                        docker compose -f docker-compose.dev.yaml up -d --wait
                        sleep 10
                        newman run tests/collection.json \
                        -e tests/environment.json --env-var "BaseUrl=http://rendez-vous.test" \
                        --delay-request 1000 --timeout-request 3000 \
                        --export-environment env.json || true
                        jq -c '.values[] | select(.key == "results")' env.json | tee newman_results.json \
                        cat newman_results.json | tee ${LOGDIR}/newman.log

                        newman run tests/access_control_check.json \
                        -e  tests/environment.json --env-var "BaseUrl=http://rendez-vous.test" \
                        --delay-request 1000 --timeout-request 3000 \
                        --export-environment env.json || true
                        jq -c '.values[] | select(.key == "results")' env.json | tee newman_ac_results.json \
                        cat newman_results.json | tee ${LOGDIR}/newman_ac.log

                        """
                    }
                }
            }
        }

        stage('DAST - owasp ZAP') {
            steps {
                script {
                    sh """
                        docker run -u root --network devsecops-demo_dev_network \
                        -v /opt/devsecops/reports:/zap/wrk:rw \
                        zaproxy/zap-weekly zap-baseline.py -t http://nginx \
                        -J zap_scan.json -r zap-report.html || true
                        cat zap_scan.json | tee ${LOGDIR}/zap_scan.log
                    """
                    
                    def zapHighAlertsCount = sh(
                        script: "jq -r '[.site[0].alerts[] | select(.riskcode == \"3\")] | length' zap_scan.json",
                        returnStdout: true
                    ).trim().toInteger()
                    
                    def zapMediumAlertsCount = sh(
                        script: 'jq -r \'[.site[0].alerts[] | select(.riskcode == "2")] | length\' zap_scan.json',
                        returnStdout: true
                    ).trim().toInteger()

                    echo "ZAP DAST Scan Summary: ${zapHighAlertsCount} High severity alerts, ${zapMediumAlertsCount} Medium severity alerts."

                    if (zapHighAlertsCount > 0) {
                        echo "SECURITY GATE FAILED: ZAP DAST detected ${zapHighAlertsCount} High severity alerts. Deployment will be blocked."
                        env.DEPLOY_ALLOWED = "false"
                    }
                    def maxAllowedZapMedium = 0
                    if (zapMediumAlertsCount > maxAllowedZapMedium) {
                        echo "QUALITY GATE FAILED: ZAP DAST detected ${zapMediumAlertsCount} Medium severity alerts, Deployment will be blocked."
                        env.DEPLOY_ALLOWED = "false"
                    }
                }
            }
        }
        
        stage('Deployment Security Gate') {
            steps {
                script {
                    if (env.DEPLOY_ALLOWED == "true") {
                        echo "All security gates passed. Proceeding with deployment."
                    } else {
                        error "Deployment blocked due to security findings. Review previous scan stages for details in logs."
                    }
                }
            }
        }
    } 

    post {
        always {
            echo "Archiving scan results and cleaning workspace..."
            archiveArtifacts artifacts: '''semgrep_scan.json, bandit_scan.json, zap-report.html, 
            pytest-full-report.json, zap_scan.json, trivy_scan.json, gitleaks_scan.json, 
            pip_audit_scan.json, trivy_iac_scan.json,newman_results, newman_ac_results''', allowEmptyArchive: true
            sh 'docker compose -f docker-compose.dev.yaml down --remove-orphans --volumes'
            cleanWs()
        }
        success {
            echo "Build ${env.BUILD_NUMBER} successfully built and passed all gates."
        }
        failure {
            echo "Build ${env.BUILD_NUMBER} failed. Check logs for details."
        }
    }
}