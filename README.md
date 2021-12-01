# tac

This is a social networking site where users can subscribe to boards and make posts. Upvoting posts past a board-specific threshold will trigger a notification for the entire community (board members) to receive.

## Compiling and building

Make sure to fill out the configuration file first before starting up the system.

The easiest way to bring up this project is using docker-compose via the command `docker-compose up --build`.

The project may also be deployed manually by locally installing dependencies:
 - Install Python dependencies via `pip install -r requirements.txt`
 - Run `run.sh` to bring up the system

## config.json file

 | Entry               | Meaning                                                               |
 |---------------------|-----------------------------------------------------------------------|
 | `port`              | The port to host the server on locally                                |
 | `secret_key`        | The Flask secret key                                                  |
 | `debug`             | Whether to run in debug mode                                          |
 | `db_link`           | The URL to the MongoDB instance                                       |
 | `vapid_public_key`  | The VAPID public key for push notifications                           |
 | `vapid_private_key` | The VAPID private key for push notifications                          |
 | `vapid_email`       | The email to use for VAPID authentication                             |

VAPID key generation can be done here: https://vapidkeys.com/.

## Project structure

| File/Folder        | Role                                                                           |
|--------------------|--------------------------------------------------------------------------------|
| .github/workflows  | Contains GitHub Actions scripts for CI/CD                                      |
| .idea              | Relevant files for PyCharm configuration                                       |
| static/            | Contains static web server files, most importantly JavaScript scripts per page |
| templates/         | Contains HTML pages for the web server                                         |
| .dockerignore      | Ignore file for Docker image construction                                      |
| .gitignore         | Ignore file for Git push                                                       |
| Dockerfile         | The web server's build script via Docker                                       |
| config-blank.json  | A skeleton version of config.json                                              |
| config.py          | Handles reading in the configuration file config.json                          |
| db.py              | Handles all database / object storage transactions                             |
| db_connect.py      | Handles creating and storing the web server's DB connection                    |
| db_test.py         | Unit tests for the database                                                    |
| docker-compose.yml | The main Docker build script for the entire project                            |
| package-lock.json  | The npm dependency lock file                                                   |
| package.json       | The npm dependency and project information file                                |
| postcss.config.js  | The dependency file for PostCSS                                                |
| requirements.txt   | The pip dependency file                                                        |
| run.sh             | A script that brings up the entire project locally                             |
| server.py          | The main web server (development) entry point                                  |
| server_api.py      | Handles API endpoints for the server                                           |
| server_auth.py     | Handles user authentication / login for the server                             |
| server_notifs.py   | Handles sending web push notifications from the server                         |
| server_webpages.py | Handles web page endpoints for the server                                      |
| tailwind.config.js | The tailwind CSS library configuration file                                    |
| wsgi.py            | The main web server (production) entry point                                   |

