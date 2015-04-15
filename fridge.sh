#!/bin/bash
# Example test script for the template that you are given

# This initialises the database:

sqlite3 fridge.db < fridge.sql

python2 iotfridge.py fridge.db < fridge.json
