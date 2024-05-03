provider "aws" {
  region     = var.AWS_REGION
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
}


resource "aws_s3_bucket" "long_term_storage_bucket" {
  bucket = "c10-railway-s3-bucket"

  tags = {
    Name        = "Long Term Storage Bucket"
    Environment = "Dev"
  }
}