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

