#!/usr/bin/env bash

geth --goerli --http --http.port=8545 \
  --http.addr=0.0.0.0 --http.vhosts="*" --allow-insecure-unlock \
  --http.api="engine,admin,eth,net,web3,personal" \
  --authrpc.addr=0.0.0.0 --authrpc.jwtsecret ./jwt.hex --authrpc.vhosts="*"
