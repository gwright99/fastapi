#! /usr/bin/env bash

# Let the DB start
echo "------ Let the DB start ------"
python ./app/backend_pre_start.py

# Run migrations
echo "------ Run alembic migration ------"
alembic upgrade head

# Create initial data in DB
echo "------ Create initial data in DB ------"
python ./app/initial_data.py