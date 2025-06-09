## Jenkins job za deploy aplikacije/docker containerjev
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/larapijemlijeko/Skupina-ZETA.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                bat 'docker-compose down'
                bat 'docker-compose up --build -d'
            }
        }
    }
}



## Jenkins instanca živi na lokalnem računalniku
java -jar jenkins.war --httpPort=9999



## Spletni del aplikacije exposamo z pomočjo ngroka, da lahko do nje dostopamo vsi (še vedno so potrebni credentiali). Policy datoteka je namenjena avtentikaciji
docker run --rm -it -v "%cd%\policy.yaml:/policy.yaml" ngrok/ngrok:latest http --url=[redacted] host.docker.internal:8080 --traffic-policy-file=policy.yaml --authtoken [redacted]



## Policy.yaml
---
on_http_request:
  - actions:
    - type: basic-auth
      config:
          credentials:
            - [redacted]