from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines.reddit_extractor import reddit_extractor
from pipelines.data_cleaner import data_cleaner
from pipelines.mongodb_insert import insert_data_to_mongodb
from jobs.spark_job import sentiment_analysis

# Default arguments for the DAG
default_args = {
    'owner': 'oussa',
    'start_date': days_ago(1),
    'retries': 1,
}

GAME = 'the last of us part 2'

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
        op_kwargs={'game': GAME},
        provide_context=True,  # Ensure the function receives context for XCom
        dag=dag
    )

    clean_reddit_data = PythonOperator(
        task_id='reddit-transform',
        python_callable=data_cleaner,
        provide_context=True,  # Ensure context is provided for XCom pull
        dag=dag
    )

    insert_data = PythonOperator(
        task_id='reddit-insert',
        python_callable=insert_data_to_mongodb,
        op_kwargs={'game_name': GAME},
        provide_context=True,  # Ensure we can use context
        dag=dag
    )

    # Spark task for sentiment analysis
    sentiment_task = SparkSubmitOperator(
        task_id='sentiment-task',
        conn_id="spark-conn",
        name='Reddit-Sentiment-Analysis',
        application="jobs/spark_job.py",
        application_args=["--game", GAME],
        dag=dag
    )

    extract_reddit_data >> clean_reddit_data >> [insert_data, sentiment_task]