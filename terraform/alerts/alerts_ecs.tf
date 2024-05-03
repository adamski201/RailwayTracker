provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY_ID
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

data "aws_iam_role" "ecs-role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_cloudwatch_log_group" "c10-railway-alerts-log-group" {
  name = "c10-railway-alerts-log-group"
}

resource "aws_cloudwatch_log_stream" "c10-railway-alerts-log-group" {
  name           = "c10-railway-alerts-log-group"
  log_group_name = aws_cloudwatch_log_group.c10-railway-alerts-log-group.name
}

resource "aws_ecs_task_definition" "trains-incidents-task-definition" {
  family                = "c10-railway-alerts-task-definition-terraform"
  container_definitions = jsonencode([
    {
      name         = "c10-railway-alerts-container"
      image        = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c10-trains-incident-alerts-repo:latest"
      essential    = true
      logConfiguration= {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "c10-railway-alerts-log-group",
        "awslogs-stream-prefix": "c10-railway-alerts-log-group",
        "awslogs-region": "eu-west-2"
      }
    }

      environment : [
        {
          "name" : "AWS_SECRET_ACCESS_KEY",
          "value" : var.AWS_SECRET_ACCESS_KEY
        },
        {
          "name" : "DB_PORT",
          "value" : var.DB_PORT
        },
        {
          "name" : "DB_USER",
          "value" : var.DB_USER
        },
        {
          "name" : "AWS_ACCESS_KEY_ID",
          "value" : var.AWS_ACCESS_KEY_ID
        },
        {
          "name" : "DB_NAME",
          "value" : var.DB_NAME
        },
        {
          "name" : "DB_HOST",
          "value" : var.DB_HOST
        },
        {
          "name" : "DB_PASS",
          "value" : var.DB_PASS
        },
        {
          "name" : "HOST",
          "value" : var.HOST
        },
        {
          "name" : "INCIDENTS_TOPIC",
          "value" : var.INCIDENTS_TOPIC
        },
        {
          "name" : "PASSWORD",
          "value" : var.PASSWORD
        },
        {
          "name" : "STOMP_PORT",
          "value" : var.STOMP_PORT
        },
        {
          "name" : "TOPIC_ARN",
          "value" : var.TOPIC_ARN
        },
        {
          "name" : "USERNAME",
          "value" : var.USERNAME
        }
      ]
    }
  ])
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = 2048
  cpu                      = 1024
  execution_role_arn       = data.aws_iam_role.ecs-role.arn
}


data "aws_vpc" "cohort-10-vpc" {
  id = var.VPC_ID
}

data "aws_ecs_cluster" "c10-ecs-cluster" {
  cluster_name = "c10-ecs-cluster"
}

data "aws_subnet" "subnet-1" {
  filter {
    name   = "tag:Name"
    values = ["cohort-10-public-subnet-1"]
  }
}

data "aws_subnet" "subnet-2" {
  filter {
    name   = "tag:Name"
    values = ["cohort-10-public-subnet-2"]
  }
}

data "aws_subnet" "subnet-3" {
  filter {
    name   = "tag:Name"
    values = ["cohort-10-public-subnet-3"]
  }
}




resource "aws_ecs_service" "alerts-service" {

  name            = "c10-railway-alerts-service-terraform"
  cluster         = data.aws_ecs_cluster.c10-ecs-cluster.id
  task_definition = aws_ecs_task_definition.trains-incidents-task-definition.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [data.aws_subnet.subnet-1.id, data.aws_subnet.subnet-2.id, data.aws_subnet.subnet-3.id]
    assign_public_ip = true
  }

  deployment_controller {
    type = "ECS"
  }
}