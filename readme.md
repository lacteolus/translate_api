# TranslationAPI
TranslationAPI can be used as a simple solution translation/thesaurus service. It utilizes third-party public services to provide translation and thesaurus functionality.
Results from external services are cached using local DB.

1. [Architecture of the solution](#architecture-of-the-solution)
2. [Pre-requisites](#pre-requisites)
   - [Google Translation API](#google-translation-api)
   - [Yandex Cloud Translate API](#yandex-cloud-translate-api)
   - [Merriam-Webster API](#merriam-webster-api)
3. [Usage](#usage)
   - [Configuration](#configuration)
      - [Logging](#logging)
   - [Production-like running](#production-like-running)
   - [Local running](#local-running)
4. [API Documentation and testing](#api-documentation-and-testing)
   - [Swagger](#swagger)
   - [Redoc](#redoc)
   - [Postman](#postman)
5. [Limitations and todos](#limitations-and-todos)

## Architecture of the solution

![Diagram](imgs/diagram.drawio.png)

Components:
1. Load balancer: Nginx
2. API/Application: FastAPI
3. DB: Redis

All components are implemented as Docker containers and can be run using `docker-compose` command.

## Pre-requisites
1. [Docker](https://www.docker.com/) should be installed on the workstation where the solution is deployed.
2. API keys and credentials for external services should be acquired in advance. 
Some services require some configurations so please read related documentation:
    - [Google Translation API](https://cloud.google.com/translate/docs/setup) 
    - [Yandex Cloud Translate API](https://cloud.yandex.com/en/docs/translate)
    - [Merriam-Webster API](https://dictionaryapi.com/products/index)

### Google Translation API
[Google Translation API](https://cloud.google.com/translate) is used to translate words and texts. 
Unfortunately it has limited functionality comparing to [Google Translate](https://translate.google.com/). 
That's why Merriam-Webster service is used additionally. Google Client Library is used for interacting with API, and it
requires [credential JSON file](https://cloud.google.com/docs/authentication/application-default-credentials) for 
authentication. Credential file must be stored as `config/google.json` file.

Example of credential file:
```json
{
  "type": "service_account",
  "project_id": "translate-401238",
  "private_key_id": "e5ceb968843d66d89456ff7f2f89f52d787c8454",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADA...QlQE4zpyxU=\n-----END PRIVATE KEY-----\n",
  "client_email": "translate-app@translate-404818.iam.gserviceaccount.com",
  "client_id": "1094544828948956146920",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/traanslate-app%40translate-402318.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

### Yandex Cloud Translate API
[Yandex Cloud Translate API]((https://cloud.yandex.com/en/docs/translate)) can be used as alternative to Google 
Translation API. It provides similar functionality and requires API key for authentication. 
API key should be added into `config/svc.yaml` file along with base API URL:
```yaml
yandex:
  api_key: "AC3NCu9n-Fp7fdTbEMEJ4QVNLTPxHdgfr2f9"
  api_base_url: "https://translate.api.cloud.yandex.net/translate/v2/translate"
```

### Merriam-Webster API
Merriam-Webster services are used to extend API functionality by adding additional information to API responses. 
Merriam-Webster provider has multiple APIs which can be used for getting language information. 
This solution utilizes [The Collegiate® Thesaurus API](https://dictionaryapi.com/products/api-collegiate-thesaurus) 
for extending responses by adding synonyms, word definitions and examples of usage to accompany main translation feature.
In order to use Merriam-Webster service, API key should be received. It's free and easy to get while your solution 
does not generate significant workload and is not used for commercial purposes.
API key should be added into `config/svc.yaml` file along with base API URL, 
which differs for their each service/dictionary:
```yaml
merriam-webster:
  api_key: "e6452f4b-45a9-47f67-2356-89815a9acc70"
  api_base_url: "https://www.dictionaryapi.com/api/v3/references/thesaurus/json"
```
## Usage
### Configuration
#### Logging
`config/logging_config.yaml` file can be used to configure logging. 
Logs format and logging level can be adjusted for different components separately within this file.

### Production-like running
You can use `docker-compose` to start the whole solution in containerized manner. 
It will build required images (if necessary) and start db, app and load balancer containers.
```commandline
docker-compose -f ./docker/compose.yaml up -d --build --scale app=N
```
Where parameter `N` is the number of backend application instances (containers) to be launched.
Without specifying `--scale` option a single application container will be launched.
For example, in order to start the solution with two application container:
```commandline
docker-compose -f ./docker/compose.yaml up -d --build --scale app=2
```
```
[+] Building 24.9s (11/11) FINISHED                                                                                                                                                                                      docker:default 
 => [app internal] load .dockerignore                                                                                                                                                                                              0.0s 
 => => transferring context: 2B                                                                                                                                                                                                    0.0s 
 => [app internal] load build definition from Dockerfile                                                                                                                                                                           0.0s 
 => => transferring dockerfile: 221B                                                                                                                                                                                               0.0s 
 => [app internal] load metadata for docker.io/library/python:3.10-alpine                                                                                                                                                          3.1s 
 => [app 1/6] FROM docker.io/library/python:3.10-alpine@sha256:28986068e3a715708b7f2e0fc4c06c748fe882fb76403424c2e854483fb45304                                                                                                    4.3s 
 => => resolve docker.io/library/python:3.10-alpine@sha256:28986068e3a715708b7f2e0fc4c06c748fe882fb76403424c2e854483fb45304                                                                                                        0.0s 
 => => sha256:28986068e3a715708b7f2e0fc4c06c748fe882fb76403424c2e854483fb45304 1.65kB / 1.65kB                                                                                                                                     0.0s 
 => => sha256:4b062a3861ac865436439499d9a03e055871a0f465833987d23b67364a35a38f 1.37kB / 1.37kB                                                                                                                                     0.0s 
 => => sha256:d19326e1ec1032d12794704db7486f49e6eb64b1a340398c451a662942722be6 6.27kB / 6.27kB                                                                                                                                     0.0s 
 => => sha256:430548f4d4bf7cdf8dc1e14a535a6ae863ecace3300d9f2b84ced5df27d88721 622.32kB / 622.32kB                                                                                                                                 0.8s 
 => => sha256:885a22b65e87121d566cfc3073f859468d93d902112d0ff218456edeb2fae22c 240B / 240B                                                                                                                                         0.3s 
 => => sha256:a975a5774afd94c2dbfda4ec2b6c75fe75649147d510034ae056dc2201e8c7bd 3.08MB / 3.08MB                                                                                                                                     2.3s 
 => => extracting sha256:430548f4d4bf7cdf8dc1e14a535a6ae863ecace3300d9f2b84ced5df27d88721                                                                                                                                          0.4s 
 => => extracting sha256:66a1fee46239226b3b105569b732a7e8663e61a2069dfa2c3e578883e8ee4264                                                                                                                                          0.6s 
 => => extracting sha256:885a22b65e87121d566cfc3073f859468d93d902112d0ff218456edeb2fae22c                                                                                                                                          0.0s 
 => => extracting sha256:a975a5774afd94c2dbfda4ec2b6c75fe75649147d510034ae056dc2201e8c7bd                                                                                                                                          0.3s 
 => [app internal] load build context                                                                                                                                                                                              0.0s 
 => => transferring context: 20.98kB                                                                                                                                                                                               0.0s 
 => [app 2/6] WORKDIR /app                                                                                                                                                                                                         0.1s 
 => [app 3/6] COPY requirements.txt .                                                                                                                                                                                              0.0s 
 => [app 4/6] RUN pip install -r requirements.txt                                                                                                                                                                                 16.1s 
 => [app 5/6] COPY app/* .                                                                                                                                                                                                         0.0s 
 => [app 6/6] RUN mkdir -p ./log                                                                                                                                                                                                   0.4s 
 => [app] exporting to image                                                                                                                                                                                                       0.7s 
 => => exporting layers                                                                                                                                                                                                            0.7s 
 => => writing image sha256:9389aa0b2ead206657cbcd29cf656e1526e5f208ff0981f3a5244919e237949c                                                                                                                                       0.0s 
 => => naming to docker.io/library/docker-app                                                                                                                                                                                      0.0s 
[+] Running 4/4
 ✔ Container redis         Running                                                                                                                                                                                                 0.0s 
 ✔ Container docker-app-1  Running                                                                                                                                                                                                 1.4s 
 ✔ Container docker-app-2  Running                                                                                                                                                                                                 1.5s 
 ✔ Container nginx         Running                                                                                                                                                                                                 0.6s 
```
To verify containers status:
```commandline
docker ps -a
```
```
CONTAINER ID   IMAGE          COMMAND                  CREATED              STATUS              PORTS                            NAMES
2e67817c75b3   nginx:latest   "/docker-entrypoint.…"   About a minute ago   Up About a minute   80/tcp, 0.0.0.0:8000->8000/tcp   nginx
fe54a02ae9fd   docker-app     "uvicorn main:app --…"   About a minute ago   Up About a minute   8000/tcp                         docker-app-2
68ad0f524895   docker-app     "uvicorn main:app --…"   About a minute ago   Up About a minute   8000/tcp                         docker-app-1
6b00df9d254c   redis:latest   "docker-entrypoint.s…"   About a minute ago   Up About a minute   6379/tcp                         redis

```
To destroy the solution:
```commandline
docker-compose -f ./docker/compose.yaml down
```
```commandline
[+] Running 5/5
 ✔ Container nginx         Removed                                                                                                                                                                                                 0.5s 
 ✔ Container docker-app-1  Removed                                                                                                                                                                                                 0.0s 
 ✔ Container docker-app-2  Removed                                                                                                                                                                                                 0.0s 
 ✔ Container redis         Removed                                                                                                                                                                                                 0.4s 
 ✔ Network docker_default  Removed  
```
By default, the solution is published on `localhost` port `8000`. Modify `docker/compose.yaml` file to 
adjust Nginx service host port if needed.

### Local running
This method can be used for testing and debugging purposes 
1. Start Redis container:
   ```commandline
   docker run --name redis -p 6379:6379 -d redis
   ```
2. Start the application:
   ```commandline
   uvicorn --app-dir app main:app --reload --port 8000 --log-config=config/logging_config.yaml
   ```
By default, application uses `localhost:6379` to connect to Redis. 
These parameters can be overwritten by creating environment variables `REDIS_HOST` and `REDIS_PORT` beforehand.

## API Documentation and testing
### Swagger
You can use automatically generated Swagger documentation by navigating to http://127.0.0.1:8000/docs

![Swagger UI](imgs/swagger.png)

### Redoc
You can use automatically generated Redoc documentation by navigating to http://127.0.0.1:8000/redoc

![Redoc UI](imgs/redoc.png)

### Postman
Postman collection can be found in `.\postman` directory. 
Use provided file `translate_api.postman_collection.json` to import collection into Postman.
In order to be able to use external API from the Postman collection, variables `yandex_key` and `mw_thesaurus_key`
should be added. They contain Yandex and Merriam-Webster API keys respectively.

![Postman UI](imgs/postman.png)

## Limitations and todos
1. Current version does not support persistent DB storage. 
All data stored in Redis DB vanishes once the Redis container restarts.
2. Docker-compose configuration support only load balancing between application containers. 
Load balancer itself and Redis DB do not support HA and can be considered as a single point of failure.
3. Security aspects are out of scope and should be considered and implemented separately.
4. Exceptions handling should be improved before going to prod.
5. Parallel processing is not implemented. Parallel requests to external services can improve general performance.
6. Only EN -> RU translations are supported
7. Not flexible and non-optimal mechanism for filtering DB items attributes is used.
8. App configuration approach should be re-factored to store all parameters in a single place