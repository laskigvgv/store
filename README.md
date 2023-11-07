# Store Project API#

This repo is the bare backend structure for the store project.

This repo will be serving the API endpoints that will be connected to the frontend.
This repo will spun up using `docker compose`. And will start the following services:
- Flask app (that will serve API endpoints)
- MongoDB database
- Postgresql database
- Redis database

We will be using the following technologies for the backend:
- Python 3.11
- Flask
- MongoDB
- Postgresql
- Redis
- Docker
- Docker Compose

## Prerequisites ##
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.11](https://www.python.org/downloads/)
- [Pipenv](https://pypi.org/project/pipenv/)
- [MongoDB Compass](https://www.mongodb.com/try/download/compass)


## Setup ##
The setup for .env files will be added later in the development process.
There we will add ports, username and passwords for the databases.

## Running the app locally ##
Make sure that you are in the root directory of the project where the app.py, Dockerfile, and docker-compose.yml files are located.

# Prerequisites #
1. [Create virtual environment](https://docs.python.org/3/library/venv.html) for Python and activate it.
2. Install dependencies: `pip install -r requirements.txt`.

# starting the app with `docker compose` 
1. Run the Flask app in a DEBUG mode:
    * `docker compose up`  
    * To rebuild the images and remove any orphaned containers, run: `docker compose up --build --remove-orphans`  
    * This will build four images and it will start four Docker containers, namely `store-redis`, `store-database`, `store-mongodb` and the app itself `store`.

# mongodb connection string 
- mongodb connection string for mongodb compass - `mongodb://127.0.0.1:27017/`

#### Some useful docker commands ####

* Remove all docker images, containers and volumes: `docker system prune --all --volumes`  
* Remove the containers from your machine: `docker-compose down`  
* List running containers: `docker ps`  
* Stop running container by id: `docker stop CONTAINER_ID`  
* Stop running container by name: `docker stop CONTAINER_NAME`  
* List all containers: `docker container ls --all`  
* List all images: `docker image ls --all`  
* Check out all options for [docker build](https://docs.docker.com/engine/reference/commandline/build/), [docker run](https://docs.docker.com/engine/reference/commandline/run/), [docker ps](https://docs.docker.com/engine/reference/commandline/ps/), [docker compose](https://docs.docker.com/compose/) and [docker docs](https://docs.docker.com/) in general.