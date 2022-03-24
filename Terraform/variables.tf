locals {
  data_lake_bucket = "project_data_lake"
}

variable "project" {
  description = "Your GCP Project ID"
  default = "final-dtc-project"
  type = string
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "us-west1"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "song_data"
}

# Copied from video:
variable "TABLE_NAME" {
  description = "BigQuery Table"
  type = string
  default = "song_data_table"
}

# Variables generally passed at runtime, unless it's optional in which case a default is defined here