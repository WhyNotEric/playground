#!/usr/bin/env bash

openssl rand -hex 32 | tr -d "\n" >"jwt.hex"
