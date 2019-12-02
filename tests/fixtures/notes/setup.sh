#!/bin/sh

# This script is temporary, while we figure out how to manage components exactly

ddc-services exec mysql mysql -psecret -e "CREATE DATABASE IF NOT EXISTS derex_notes"
ddc-project run --rm notes ./manage.py migrate
