(rough draft)

### Problem Description

I wanted to see what qualities of a song lead to popularity, and how that has changed over time. I used weekly top 100 chart data from the US from 196? to 2018, and filtered to just the number one song each week. This knowledge is desireable for folks in the music industry, like producers and such.

The data included the following fields:
key
valence
etc...

I narrowed down which fields to use when putting together my dashboard, as visua


### Ingestion to Data Lake

I used Terraform as IaC, and Airflow for workflow orchestration (batch data). This first round of DAGs completes the following tasks:
Downloads the zip files
Extracts the csvs
Converts them to parquet
Uploads them to GCS
Creates external BQ tables from them

(A: Used two separate DAGs for ease, since data )

At this point, I explored the data a bit with the BQ UI. I tried making partitioned/clustered tables (using these __ fields), but the query performance was unaffected, so I decided not to move forward with that. (B: I made tables with the BQ UI using these commands: __)


### Transformation in Data Warehouse

Option A) I ran a second DAG that ran the following tasks (on Google VM?):
Created internal tables from external?
Spark job to transform the data, then send transformed data to BQ storage


Option B) I was unable to spend time fixing the issues related to itegrating Spark with Airflow, so I followed these steps to run PySpark with the Dataproc Cluster UI:
Commisioned cluster with GCP terminal window with this command __
Went to web interfaces > Jupyter > GCS > created .ipynb


### Dashboard

I used Google Data Studio to put together my dashboard. I chose to work with valence for the one to track over time, because __ . I settled on key as the categorical variable, because __ . I also chose to focus on the time period of 2015-2018, since (data look prettier and easier that way), and most recent times are more relevant.

Based on these visuals, it appears that people in the US hate D# and wanted to be sad in 2016-2018. 






