<p align="center">
<img src="https://github.com/FedericoGianni/run-with-me-be/blob/main/deliverables/logo_gradient.png">
</p>

### Requirements
* Docker [Docker Installation Guide](https://docs.docker.com/get-docker/)  
* Docker-Compose  [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### Usage

Uses gunicorn + nginx.

1. Rename *.env.prod-sample* to *.env.prod* and *.env.prod.db-sample* to *.env.prod.db*. Update the environment variables.
1. Build the images and run the containers:

    ```sh
    $ docker-compose -f docker-compose.yml up -d --build
    ```

    Test it out at [http://localhost:1337](http://localhost:1337). No mounted folders. To apply changes, the image must be re-built.
    
    
    In case of errors, chmod +x on entrypoint.prod.sh
