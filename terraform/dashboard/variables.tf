variable "AWS_ACCESS_KEY_ID" {
  type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
}

variable "AWS_REGION" {
  type = string
}

variable "DB_HOST" {
  type = string
}

variable "DB_PORT" {
  type = string
}

variable "DB_USER" {
  type = string
}

variable "DB_PASS" {
  type      = string
  sensitive = true
}

variable "DB_NAME" {
  type = string
}

variable "VPC_ID" {
  type = string
}

variable "TOPIC_ARN" {
  type = string
}

