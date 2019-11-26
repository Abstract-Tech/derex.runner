#!/bin/sh

# This script is temporary, while we figure out how to manage components exactly

ddc exec mysql mysql -psecret -e "CREATE DATABASE IF NOT EXISTS derex_notes"
ddc-local run --rm notes ./manage.py migrate
