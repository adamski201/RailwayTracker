data "aws_iam_policy_document" "archive-schedule-permissions-policy" {

  statement {
    effect = "Allow"

    resources = [
      aws_lambda_function.archive-lambda.arn,
      "${aws_lambda_function.archive-lambda.arn}:*"
    ]

    actions = ["lambda:InvokeFunction"]
  }
}

resource "aws_iam_role" "archive-schedule-role" {
  name               = "c10-railway-schedule-role-archive"
  assume_role_policy = data.aws_iam_policy_document.schedule-trust-policy.json

  inline_policy {
    name   = "c10-railway-inline-lambda-execution-policy-archive"
    policy = data.aws_iam_policy_document.archive-schedule-permissions-policy.json
  }
}

resource "aws_scheduler_schedule" "archive-schedule" {
  name                = "c10-archive-archive-schedule"
  group_name          = "default"
  schedule_expression = "cron(0 9 1 * ? *)"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.archive-lambda.arn
    role_arn = aws_iam_role.archive-schedule-role.arn
  }
}
