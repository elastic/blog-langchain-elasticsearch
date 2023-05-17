#!/bin/sh

## load the environment variables
source .env

python3 step-1A-scrape-urls.py
python3 step-1B-scrape-content.py
