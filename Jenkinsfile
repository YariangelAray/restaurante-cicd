// Pipeline CI/CD del sistema de pedidos y reservas del restaurante
pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()
    }

    parameters {
        string(name: 'PUERTO_PRODUCCION', defaultValue: '8089',
               description: 'Puerto del computador donde se publica la versión de producción')
    }

    triggers {
        // Revisa GitHub cada minuto y arranca si hay cambios en main
        pollSCM('* * * * *')
    }

    environment {
        IMAGEN         = "restaurante:${env.BUILD_NUMBER}"
        RED            = 'cicd'
        STAGING        = 'restaurante-staging'
        APP_URL        = 'http://restaurante-staging:5000'
        SELENIUM_URL   = 'http://selenium:4444/wd/hub'
        SONAR_HOST_URL = 'http://sonarqube:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Preparar entorno') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --quiet --upgrade pip
                    pip install --quiet -r requirements-dev.txt
                    mkdir -p reportes
                '''
            }
        }

        stage('Calidad de código') {
            steps {
                sh '. .venv/bin/activate && flake8 app tests carga'
            }
        }

        stage('Seguridad') {
            parallel {
                stage('Análisis estático (Bandit)') {
                    steps {
                        sh '. .venv/bin/activate && bandit -r app -ll'
                    }
                }
                stage('Dependencias (pip-audit)') {
                    steps {
                        sh '. .venv/bin/activate && pip-audit -r requirements.txt'
                    }
                }
            }
        }

        stage('Pruebas unitarias y de API') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest tests/unit tests/api --junitxml=reportes/pruebas.xml \
                           --cov=app --cov-report=xml:coverage.xml
                '''
            }
        }

        stage('Análisis SonarQube') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        docker run --rm -u root --network $RED --volumes-from jenkins -w "$WORKSPACE" \
                            -e SONAR_HOST_URL=$SONAR_HOST_URL -e SONAR_TOKEN=$SONAR_TOKEN \
                            sonarsource/sonar-scanner-cli
                    '''
                }
            }
        }

        stage('Construir imagen') {
            steps {
                sh 'docker build -t $IMAGEN .'
            }
        }

        stage('Desplegar en staging') {
            steps {
                sh '''
                    docker rm -f $STAGING || true
                    docker run -d --name $STAGING --network $RED $IMAGEN
                    for i in $(seq 1 20); do
                        curl -sf $APP_URL/salud && exit 0
                        sleep 2
                    done
                    echo "Staging no respondió"
                    exit 1
                '''
            }
        }

        stage('Pruebas en staging') {
            parallel {
                stage('Interfaz (Selenium)') {
                    steps {
                        sh '. .venv/bin/activate && pytest tests/ui --junitxml=reportes/interfaz.xml'
                    }
                }
                stage('Carga (Locust)') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            locust -f carga/locustfile.py --headless -u 20 -r 5 -t 20s \
                                   --host $APP_URL --csv reportes/carga --only-summary
                        '''
                    }
                }
            }
        }

        stage('Aprobación') {
            steps {
                input message: '¿Desplegar esta versión en producción?', ok: 'Desplegar'
            }
        }

        stage('Desplegar en producción') {
            steps {
                sh """
                    docker rm -f restaurante-prod || true
                    docker run -d --name restaurante-prod -p ${params.PUERTO_PRODUCCION}:5000 ${env.IMAGEN}
                """
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reportes/*.xml'
            archiveArtifacts artifacts: 'reportes/*.csv', allowEmptyArchive: true
        }
        success {
            echo "Versión publicada en http://localhost:${params.PUERTO_PRODUCCION}"
        }
        failure {
            echo 'El pipeline falló. Revisa la etapa en rojo y su registro.'
        }
    }
}
