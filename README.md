# skin-assist-api

### Docker RUN Instructions

[1] - Copy env-file_template file, fill in, then save as "env-file"

[2] - Make sure firebase_private_key.json file, firebase_config.json file and DB_PASSWORD are in https://console.cloud.google.com/security/secret-manager. Generate from firebase if necessary

[3] - Make sure docker daemon is running

[4] - Build Container Image with "docker build -t app_image ."

[5] - Make sure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set on your machine and points to your ADC json file (https://cloud.google.com/docs/authentication/provide-credentials-adc#attached-sa)

[6] - Run Container with "docker run --env-file env-file --restart unless-stopped -p 8000:8000 -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/application_default_credentials.json:ro app_image"

[7] - If pdb debugging needed, run container with attached terminal "docker run -it --env-file env-file --restart unless-stopped -p 8000:8000 -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/application_default_credentials.json:ro app_image"

[8] - To enter an interactive session "docker run -it --env-file env-file --restart unless-stopped -p 8000:8000 -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/application_default_credentials.json:ro app_image /bin/bash"

### Docker COMPOSE Instructions
Docker Compose alternative (good for env variables requiring substitution, can't inject config files like google credentials json):

[1] - Copy .env_template file, fill in, then save as ".env"

[2] - Make sure docker daemon is running

[3] - Build Container Image with "docker build -t app_image ."

[4] - Run Container with Docker Compose "docker-compose up"
