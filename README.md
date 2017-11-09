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


Details

The web image is a simple flask + wtforms app that takes some input from a browser.
It uses this to construct a heroku api call via the heroku-cli tool, which spawns the worker.

The worker is a standard algo container running in alpine linux, preconfigured with depends.
After the worker is spawned, it will run in the background and spin up the instances.
