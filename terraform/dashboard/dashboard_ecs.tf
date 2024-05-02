data "aws_iam_role" "ecs-role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "dashboard-task-definition" {
  family                = "c10-railway-dashboard"
  container_definitions = jsonencode([
    {
      name         = "dashboard"
      image        = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/railway-dashboard:latest"
      essential    = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ],

      environment : [
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : var.AWS_SECRET_ACCESS_KEY
        },
        {
          "name" : "DB_USER",
          "value" : var.DB_USER
        },
        {
          "name" : "ACCESS_KEY_ID",
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

# Starts dashboard service

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

resource "aws_security_group" "dashboard-security_group" {
  name        = "c10-railway-dashboard-sg"
  description = "Allows access through port 8501 for the dashboard"
  vpc_id      = data.aws_vpc.cohort-10-vpc.id

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 8501
    protocol    = "tcp"
    to_port     = 8501
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    protocol    = "tcp"
    to_port     = 80
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_service" "dashboard-service" {

  name            = "c10-railway-dashboard-service-terraform"
  cluster         = data.aws_ecs_cluster.c10-ecs-cluster.id
  task_definition = aws_ecs_task_definition.dashboard-task-definition.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [data.aws_subnet.subnet-1.id, data.aws_subnet.subnet-2.id, data.aws_subnet.subnet-3.id]
    security_groups  = [aws_security_group.dashboard-security_group.id]
    assign_public_ip = true
  }

  deployment_controller {
    type = "ECS"
  }
}

