#!/bin/sh


curl -vvv --request GET \
  --url 'http://10.141.39.13/api/v1/auth/clients' \
  --header 'accept: application/json' | jq


#  --header 'authorization: Bearer XXX' 
