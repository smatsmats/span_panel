#!/bin/sh

# set the panel's ip address in IP in the environment
# something like:
# export IP='10.0.0.X'

curl -vvv --request GET \
  --url "http://${IP}/api/v1/status" \
  --header "accept: application/json" | jq

