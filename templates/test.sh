#!/bin/bash
# Example test script for the template that you are given

# This initialises the database:
sqlite3 test.db < test.sql

python2 iotfridge_template.py test.db < test.json
