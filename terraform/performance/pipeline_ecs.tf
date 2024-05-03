resource "aws_iam_role" "ecs_role" {
  name = "c10-railway-performance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect = "Allow"
      },
    ]
  })
}

data  "aws_iam_policy_document" "example-schedule-trust-policy" {

    statement {
        effect = "Allow"

        principals {
            type        = "Service"
            identifiers = ["scheduler.amazonaws.com"]
        }

        actions = ["sts:AssumeRole"]
    }
}

# A permissions policy that allows things-attached-to-the-attached-role to do things
data  "aws_iam_policy_document" "example-schedule-permissions-policy" {

    statement {
        effect = "Allow"

        resources = [
            aws_ecs_task_definition.performance_pipeline_task.arn,
            "${aws_ecs_task_definition.performance_pipeline_task.arn}:*"
        ]

        actions = [
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:DescribeTasks"
        ]
    }
}

resource "aws_iam_role" "schedule-role" {
    name               = "schedule-role-terraform"
    assume_role_policy = data.aws_iam_policy_document.example-schedule-trust-policy.json
    inline_policy {
      name = "ecs-execution-policy"
      policy = data.aws_iam_policy_document.example-schedule-permissions-policy.json
    }
}

resource "aws_ecs_task_definition" "performance_pipeline_task" {
  family                   = "c10-railway-performance-terraform"
  execution_role_arn       = aws_iam_role.ecs_role.arn
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  container_definitions    = jsonencode([
    {
      name         = "railway-performance-pipeline"
      image        = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/railway-performance-pipeline:latest"
      cpu          = 0
      essential    = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
          appProtocol   = "http"
        }
      ]
      environment = [
        {
          name  = "REALTIME_API_USER"
          value = var.RTT_API_USER
        },
        {
          name  = "REALTIME_API_PASS"
          value = var.RTT_API_PASS
        },
        {
          name  = "DB_PORT"
          value = var.DB_PORT
        },
        {
          name  = "DB_USER"
          value = var.DB_USER
        },
        {
          name  = "DB_NAME"
          value = var.DB_NAME
        },
        {
          name  = "DB_HOST"
          value = var.DB_HOST
        },
        {
          name  = "DB_PASSWORD"
          value = var.DB_PASS
        }
      ]
    }
  ])
}


resource "aws_scheduler_schedule" "cron" {
  name        = "c10-railway-performance-schedule-terraform"
  group_name  = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(30 0 * * ? *)"

  target {
    arn      = var.CLUSTER_ARN
    role_arn = aws_iam_role.schedule-role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.performance_pipeline_task.arn
      launch_type         = "FARGATE"

      network_configuration {
        assign_public_ip = true
        subnets          = var.SUBNET_IDS
      }
    }
  }
}