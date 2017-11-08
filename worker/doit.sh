#!/bin/bash
source env/bin/activate && ansible-playbook deploy.yml -t digitalocean,vpn,cloud -e "do_access_token=${DO_ACCESS_TOKEN} do_server_name=${DO_SERVER_NAME} do_region=${DO_REGION}"