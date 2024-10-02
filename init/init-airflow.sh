#!/bin/bash
set -e

# Install requirements
pip install -r /opt/airflow/requirements.txt

# Initialize the database
airflow db init
airflow db upgrade

# Create the Airflow admin user
airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email airflow@airflow.com \
    --password admin