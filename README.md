# AlgoVPNGen
AlgoVPNGen - Algo VPN Generator
Continuous Deployment Repo

To build and run locally:

make image.web && make image.worker

To run web locally:

make run.web

Test a worker container run:

make run.worker


Web container will bind the application server to $PORT as per heroku runtime

CircleCI config in .circleci

Using flask, python3, uwsgi, nginx


## Details

The web image is a simple flask + wtforms app (/app) that takes some input from a browser.
It uses this to construct a heroku api call via the heroku-cli tool, which spawns the worker container (/worker/doit.sh).

The worker is a standard algo container running in alpine linux, preconfigured with depends.
After the worker is spawned, it will run in the background and spin up the instances.
Standard output from the container is sent to the web client via a websocket connection (using SocketIO).

After execution of algo, contents of the data directory is displayed as base64 encoded blob.
The command to convert this back to a file in linux, macos and windows is then displayed.

## CD Build

The .circleci contains the CD instructions to deploy /app and /worker containers into heroku.


## Threat Model and Security
The web application itself has a limited input surface area for user input, tokens and params.
These are all validated by WTForms, which should prevent unsafe characters from being injected.
Additionally, the input command is sanitized with shlex.quote().

## Privacy
This tool requires access to your cloud provider access code, usually an API key or Access/Secret Key.
It is stored temporarily in a server side session object with a lifetime of 1 hour.
This is not logged during runtime of the application, and it cleared from the sesion as soon as the build has begin.

The runtime environment of the app is a Docker container on the Heroku infrastructure. Because containers are ephemeral,
it is possible the session data may be cleared even more frequently than 1 hour.

## Thank you
* Trail of bits for creating algo
* Strongswan
* CircleCI
* Heroku
* Dan from ToB

## References
https://mrl33h.de/post/21 Handling modal forms with Flask
https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
https://github.com/trailofbits/algo/pull/331 Docker PR for algo

Logo generated with https://logomakr.com