import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
# from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = 'song_data'

DATASET = "songs"
FILES = ['acoustic_features', 'song_chart']
INPUT_PART = "raw"
INPUT_FILETYPE = "parquet"

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="gcs_2_bq_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    for item in FILES:
        # move_files_gcs_task = GCSToGCSOperator(
        #     task_id=f'move_{item}_task',
        #     source_bucket=BUCKET,
        #     source_object=f'{INPUT_PART}/{item}*.{INPUT_FILETYPE}',
        #     destination_bucket=BUCKET,
        #     destination_object=f'{DATASET}',
        #     move_object=True
        # )

        # bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        #     task_id=f"bq_{colour}_{DATASET}_external_table_task",
        #     table_resource={
        #         "tableReference": {
        #             "projectId": PROJECT_ID,
        #             "datasetId": BIGQUERY_DATASET,
        #             "tableId": f"{colour}_{DATASET}_external_table",
        #         },
        #         "externalDataConfiguration": {
        #             "autodetect": "True",
        #             "sourceFormat": f"{INPUT_FILETYPE.upper()}",
        #             "sourceUris": [f"gs://{BUCKET}/{colour}/*"],
        #         },
        #     },
        # )


        CREATE_BQ_TBL_QUERY = (
            f"CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.{item} \
            AS \
            SELECT * FROM {BIGQUERY_DATASET}.{item}_external_table;"
        )

        # Create internal table from external table
        bq_create_internal_table_job = BigQueryInsertJobOperator(
            task_id=f"bq_create_{item}_internal_table_task",
            configuration={
                "query": {
                    "query": CREATE_BQ_TBL_QUERY,
                    "useLegacySql": False,
                }
            }
        )


        pyspark_submit_job = SparkSubmitOperator(
            application="../Spark/Transform_in_warehouse.py",
            task_id="pyspark_submit_job"
        )



        bq_create_internal_table_job >> pyspark_submit_job
