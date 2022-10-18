#!/usr/bin/env bash

docker-compose -f create-account.yaml run validator-import-launchpad

docker-compose -f create-account.yaml run validator-import-launchpad-2
