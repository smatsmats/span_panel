#!/bin/sh

# set the panel's ip address in IP in the environment
# something like:
# export IP='10.0.0.X'

curl -vvv --request POST \
  --url "http://${IP}/api/v1/auth/clients" \
  --header "accept: application/json" | jq


#  --header 'authorization: Bearer XXX' 
