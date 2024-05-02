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

variable "SUBNET_GROUP" {
    type = string
}

variable "VPC_ID" {
    type = string
}

variable "DB_USER" {
    type = string
}

variable "DB_PASS" {
    type = string
}

variable "PUBLIC_SUBNET_ID" {
    type = string
}