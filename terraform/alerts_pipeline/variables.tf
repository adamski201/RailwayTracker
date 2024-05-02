variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}

variable "AWS_ACCESS_KEY_ID" {
    type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
    type = string
}

variable "HOST" {
    type = string
}

variable "STOMP_PORT" {
    type = string
    default = "5439"
}

variable "USERNAME" {
    type = string
}

variable "PASSWORD" {
    type = string
}

variable "INCIDENTS_TOPIC" {
    type = string
}

variable "TOPIC_ARN" {
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
    type = string
}

variable "DB_NAME" {
    type = string
}

variable "VPC_ID" {
    type = string
}