
### Development

Uses the default Flask development server.

1. Rename *.env.dev-sample* to *.env.dev*.
1. Update the environment variables in the *docker-compose.yml* and *.env.dev* files.
    - (M1 chip only) Remove `-slim-buster` from the Python dependency in `services/web/Dockerfile` to suppress an issue with installing psycopg2
1. Build the images and run the containers:

    ```sh
    $ docker-compose up -d --build
    ```

    Test it out at [http://localhost:5000](http://localhost:5000). The "web" folder is mounted into the container and your code changes apply automatically.
    
    In case of errors, chmod +x on entrypoint.sh

### Production

Uses gunicorn + nginx.

1. Rename *.env.prod-sample* to *.env.prod*, *.env.prod.db-sample* to *.env.prod.db* and *.env.prod.dbgui-sample* to *.env.prod.dbgui*. Update the environment variables.
1. Build the images and run the containers:

    ```sh
    $ docker-compose -f docker-compose.prod.yml up -d --build
    ```

    Test it out at [http://localhost:1337](http://localhost:1337). No mounted folders. To apply changes, the image must be re-built.
    
    
    In case of errors, chmod +x on entrypoint.prod.sh
