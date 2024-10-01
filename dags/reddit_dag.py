from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines.reddit_extractor import reddit_extractor
from pipelines.data_cleaner import data_cleaner

# Default arguments for the DAG
default_args = {
    'owner': 'oussa',
    'start_date': days_ago(1),
    'retries': 1,
}

# Define the DAG
with DAG(
    'reddit_extraction_dag',
    default_args=default_args,
    schedule_interval='*/5 * * * *',  # Run every 5 minutes
    catchup=False
) as dag:

    extract_reddit_data = PythonOperator(
        task_id='reddit_extract',
        python_callable=reddit_extractor,
        op_kwargs={'game': 'the last of us part 2'},
        provide_context=True,  # Ensure the function receives context for XCom
        dag=dag
    )

    clean_reddit_data = PythonOperator(
        task_id='reddit-transform',
        python_callable=data_cleaner,
        provide_context=True,  # Ensure context is provided for XCom pull
        dag=dag
    )

    extract_reddit_data >> clean_reddit_data