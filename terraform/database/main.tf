provider "aws" {
    region = "eu-west-2"
    access_key = var.AWS_ACCESS_KEY_ID
    secret_key = var.AWS_SECRET_ACCESS_KEY
}


data "aws_db_subnet_group" "public_subnet_group" {
    name = var.SUBNET_GROUP
}

data "aws_vpc" "cohort_10_vpc" {
    id = var.VPC_ID
}


resource "aws_db_instance" "trains-db" {
  allocated_storage    = 10
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.t3.micro"
  db_name                 = "postgres"
  username             = "postgres"
  password             = "railway_tracker_123"
  parameter_group_name = "default.postgres12"


  vpc_security_group_ids = [aws_security_group.trains-db-sg.id]
}


resource "aws_security_group" "trains-db-sg" {
  name = "terraform-example-instance"
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}