variable "AWS_ACCESS_KEY_ID" {
  type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
}

variable "AWS_REGION" {
  type    = string
  default = "eu-west-2"
}


variable "DB_HOST" {
  description = "Database host URL"
  type        = string
}

variable "DB_NAME" {
  description = "Database name"
  type        = string
}

variable "DB_PASS" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "DB_PORT" {
  description = "Database port"
  type        = string
}

variable "DB_USER" {
  description = "Database user"
  type        = string
}

variable "RTT_API_PASS" {
  description = "RTT pass"
  type        = string
}

variable "RTT_API_USER" {
  description = "RTT user"
  type        = string
}


variable "CLUSTER_ARN" {
  description = "Cluster ARN"
  type        = string
}

variable "SUBNET_IDS" {
  description = "Subnet IDs"
  type        = list(string)
}