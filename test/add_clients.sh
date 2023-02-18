#!/bin/sh


curl -vvv --request POST \
  --url 'http://10.141.39.13/api/v1/auth/register' \
  --data '{ "name": "SPAN_API_User_2", "description": "SPAN_API_User_2 description" }' \
  --header 'accept: application/json' | jq

#  --header 'authorization: Bearer XXX' \

