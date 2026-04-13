provider "google" {
  project = var.project_id
  region  = var.gcs_location
}

# Raw storage bucket (immutable JSON)
resource "google_storage_bucket" "raw_bucket" {
  name     = var.gcs_bucket_name
  location = var.gcs_location

  uniform_bucket_level_access = true
}

# Raw dataset (ingestion layer)
resource "google_bigquery_dataset" "raw" {
  dataset_id = var.raw_dataset_id
  location   = var.bq_location
}

# Analytics dataset (dbt models)
resource "google_bigquery_dataset" "analytics" {
  dataset_id = var.analytics_dataset_id
  location   = var.bq_location
}
