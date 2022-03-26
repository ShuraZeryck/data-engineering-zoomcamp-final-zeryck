import os
import logging
from zipfile import ZipFile

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")


dataset_url = 'https://zenodo.org/record/4904639/files/musicoset_popularity.zip'
dataset_folder = 'musicoset_popularity'
dataset_file = 'song_chart.csv'
parquet_file = 'song_chart.parquet'
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = 'song_data'


def extract_from_zip(path_to_file, path_to_readme):
    with ZipFile('musicoset_popularity.zip', 'r') as zipObj:
        zipObj.extract(path_to_file)
        zipObj.extract(path_to_readme)


def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in csv format, for the moment")
        return
    po = pv.ParseOptions(delimiter='\t')
    table = pv.read_csv(src_file, parse_options=po)
    pq.write_table(table, src_file.replace('.csv', '.parquet'))


def upload_to_gcs(bucket, object_name, local_file, local_readme_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed (https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob1 = bucket.blob(object_name)
    blob1.upload_from_filename(local_file)

    blob2 = bucket.blob('raw/Pop_ReadMe.txt')
    blob2.upload_from_filename(local_readme_file)


default_args = {
    "owner": "airflow",
    "start_date": days_ago(0),
    "depends_on_past": False,
    "retries": 1,
}



with DAG(
    dag_id="gcs_ingestion_dag_song_pop_v02",
    schedule_interval="@once",
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"curl -sSLf {dataset_url} > {path_to_local_home}/{dataset_folder}.zip"
    )

    extract_from_zip_task = PythonOperator(
        task_id="extract_from_zip_task",
        python_callable=extract_from_zip,
        op_kwargs={
            "path_to_file": f"{dataset_folder}/{dataset_file}",
            "path_to_readme": f"{dataset_folder}/ReadMe.txt"
        },
    )


    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{path_to_local_home}/{dataset_folder}/{dataset_file}",
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{path_to_local_home}/{dataset_folder}/{parquet_file}",
            "local_readme_file": f"{path_to_local_home}/{dataset_folder}/ReadMe.txt"
        },
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table_song_pop",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
            },
        },
    )


download_dataset_task >> extract_from_zip_task >> format_to_parquet_task >> local_to_gcs_task >> bigquery_external_table_task