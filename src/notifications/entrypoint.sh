#!/bin/bash

# Keep the python server in a loop
while true
do
    python $(dirname $0)/server.py
    sleep 5
done