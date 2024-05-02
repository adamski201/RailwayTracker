data "aws_iam_policy_document" "reports-schedule-permissions-policy" {

  statement {
    effect = "Allow"

    resources = [
      aws_lambda_function.reports-lambda.arn,
      "${aws_lambda_function.reports-lambda.arn}:*"
    ]

    actions = ["lambda:InvokeFunction"]
  }
}

resource "aws_iam_role" "reports-schedule-role" {
  name               = "c10-railway-schedule-role-reports"
  assume_role_policy = data.aws_iam_policy_document.schedule-trust-policy.json

  inline_policy {
    name   = "c10-railway-inline-lambda-execution-policy-reports"
    policy = data.aws_iam_policy_document.reports-schedule-permissions-policy.json
  }
}

resource "aws_scheduler_schedule" "reports-schedule" {
  name                = "c10-railway-reports-schedule-terraform"
  group_name          = "default"
  schedule_expression = "cron(0 9 1 * ? *)"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.reports-lambda.arn
    role_arn = aws_iam_role.reports-schedule-role.arn
  }
}
