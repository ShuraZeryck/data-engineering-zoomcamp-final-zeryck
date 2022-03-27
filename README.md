(rough draft)

### Problem Description

For this project, I wanted to see what qualities of a song lead to popularity, and how that has changed over time. This knowledge is useful for people in the music industry, such as pop artists and producers. I used data from the Billboard Hot 100 (a weekly-updated list of top songs in the US), with records from 1964 to 2018.

One of the files, song_chart, lists the top 100 songs from each week. The other, acoustic_features, contains an entry for each individual song with fields describing its musicality. The following fields interested me the most:

1. key: A, A#, B, etc.
2. mode: Major or minor
3. danceability: “how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity”
4. energy: “a perceptual measure of intensity and activity”
5. valence: “musical positiveness conveyed by a track”

Full descriptions of all fields are located in the ReadMe files, which are uploaded to GCS in the data ingestion step.


### Ingestion to Data Lake

I used Terraform for IaC, and Airflow for workflow orchestration. My DAGs completed the following tasks:

1. Retrieve zip files from the data source
2. Extract desired CSVs and ReadMe files from the zip archives 
3. Convert CSVs to parquet
4. Upload the files to GCS
5. Create external BigQuery tables from the parquet files (Note: song_chart became song_pop, and acoustic_features became song_feat)

At this point, I explored the data a bit with the BigQuery SQL workspace. I tried partitioning the song_pop table by week and the song_feat table by mode, but this did not improve query performance, so I decided not to move forward with that.

I made tables with the following SQL statements:

```
CREATE OR REPLACE TABLE `final-dtc-project.song_data.song_feature_data`
AS SELECT * FROM `final-dtc-project.song_data.external_table_song_feat`;

CREATE OR REPLACE TABLE `final-dtc-project.song_data.song_popularity_data`
AS SELECT * FROM `final-dtc-project.song_data.external_table_song_pop`;
```

### Transformation in Data Warehouse

I was unable to fix the issues related to itegrating Spark and BigQuery, so I took the following steps to run a Spark job using Dataproc (ref: https://medium.com/google-cloud/apache-spark-and-jupyter-notebooks-made-easy-with-dataproc-component-gateway-fa91d48d6a5a):

Opened a terminal window in my GCP console, and enabled the required APIs with the following command:

```
gcloud services enable dataproc.googleapis.com \
  compute.googleapis.com \
  storage-component.googleapis.com \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com
```

Still in the terminal, I ran the following to commission a Dataproc cluster:

```
REGION=us-west1
```
```
CLUSTER_NAME=dproc-cluster
```
```
 gcloud beta dataproc clusters create ${CLUSTER_NAME} \
     --region=${REGION} \
     --master-machine-type e2-standard-2 \
     --worker-machine-type e2-standard-2 \
     --image-version 1.5-debian \
     --initialization-actions gs://dataproc-initialization-actions/python/pip-install.sh \
     --metadata 'PIP_PACKAGES=google-cloud-storage google-cloud-bigquery' \
     --optional-components=ANACONDA,JUPYTER \
     --enable-component-gateway
```

3. I then navigated to my Dataproc cluster in the console, went to “Web Interfaces,” clicked on Jupyter, and created a python3 notebook in the GCS folder.



### Dashboard

I used Google Data Studio to put together my dashboard. I chose to work with valence for the one to track over time, because __ . I settled on key as the categorical variable, because __ . I also chose to focus on the time period of 2015-2018, since (data look prettier and easier that way), and most recent times are more relevant.

https://datastudio.google.com/reporting/b77b7528-3e73-48fa-8bee-dad34a9e8641

Based on these visuals, it appears that people in the US hate D# and wanted to be sad in 2016-2018. 






