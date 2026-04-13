variable "project_id" {
  type = string
}

variable "gcs_bucket_name" {
  type = string
}

variable "gcs_location" {
  type    = string
  default = "US"
}

variable "bq_location" {
  type    = string
  default = "US"
}

variable "raw_dataset_id" {
  type    = string
  default = "spotify_pipeline"
}

variable "analytics_dataset_id" {
  type    = string
  default = "spotify_analytics"
}
