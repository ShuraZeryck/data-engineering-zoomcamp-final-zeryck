(rough draft)

### Problem Description

For this project, I wanted to see what qualities of a song lead to popularity, and how that has changed over time. This knowledge is useful for people in the music industry, such as pop artists and producers. I used data from the Billboard Hot 100 (a weekly-updated list of top songs in the US), with records from 1964 to 2018.

The dataset included information on a number of musical qualities for each song. The following fields interested me the most:

1. key: A, A#, B, etc.
2. mode: Major or minor
3. danceability: “how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity”
4. energy: “a perceptual measure of intensity and activity”
5. valence: “musical positiveness conveyed by a track”

Full descriptions of all fields are located in the ReadMe files, which are uploaded to GCS in the data ingestion step.


### Ingestion to Data Lake

I used Terraform as IaC, and Airflow for workflow orchestration (batch data). This first round of DAGs completes the following tasks:

1. Downloads the zip files
2. Extracts the csvs, and ReadMes
3. Converts the csvs to parquet
4. Uploads the files to GCS
5. Creates external BQ tables from the parquets

At this point, I explored the data a bit with the BQ UI. I tried making partitioned/clustered tables (using these __ fields), but the query performance was unaffected, so I decided not to move forward with that. I made tables with the BQ UI using these commands:

CREATE OR REPLACE TABLE `final-dtc-project.song_data.song_feature_data`
AS SELECT * FROM `final-dtc-project.song_data.external_table_song_feat`;

CREATE OR REPLACE TABLE `final-dtc-project.song_data.song_popularity_data`
AS SELECT * FROM `final-dtc-project.song_data.external_table_song_pop`;


### Transformation in Data Warehouse

I was unable to spend time fixing the issues related to itegrating Spark+Airflow+BQ, so I followed these steps to run PySpark with the Dataproc Cluster UI:

1. Commisioned cluster with GCP terminal window with this command

gcloud services enable dataproc.googleapis.com \
  compute.googleapis.com \
  storage-component.googleapis.com \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com

REGION=us-west1

CLUSTER_NAME=dproc-cluster

 gcloud beta dataproc clusters create ${CLUSTER_NAME} \
     --region=${REGION} \
     --master-machine-type e2-standard-2 \
     --worker-machine-type e2-standard-2 \
     --image-version 1.5-debian \
     --initialization-actions gs://dataproc-initialization-actions/python/pip-install.sh \
     --metadata 'PIP_PACKAGES=google-cloud-storage google-cloud-bigquery' \
     --optional-components=ANACONDA,JUPYTER \
     --enable-component-gateway


2. Went to web interfaces > Jupyter > GCS > created python3 notebook


### Dashboard

I used Google Data Studio to put together my dashboard. I chose to work with valence for the one to track over time, because __ . I settled on key as the categorical variable, because __ . I also chose to focus on the time period of 2015-2018, since (data look prettier and easier that way), and most recent times are more relevant.

https://datastudio.google.com/reporting/b77b7528-3e73-48fa-8bee-dad34a9e8641

Based on these visuals, it appears that people in the US hate D# and wanted to be sad in 2016-2018. 






