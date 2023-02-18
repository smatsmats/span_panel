#!/bin/sh


curl -vvv --request GET \
  --url 'http://10.141.39.13/api/v1/status' \
  --header 'accept: application/json' | jq

