resource "aws_iam_role" "reports-lambda-role" {
  name               = "c10-railway-reports-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda-role-policy.json
}

data "aws_ecr_repository" "reports-lambda-ecr-repo" {
  name = "c10-railway-report-repo"
}

data "aws_ecr_image" "reports-lambda-image" {
  repository_name = data.aws_ecr_repository.reports-lambda-ecr-repo.name
  image_tag       = "latest"
}

resource "aws_lambda_function" "reports-lambda" {
  role          = aws_iam_role.reports-lambda-role.arn
  function_name = "c10-railway-reports-lambda-terraform"
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.reports-lambda-image.image_uri
  memory_size   = 256
  timeout       = 600
  environment {
    variables = {
      ACCESS_KEY_ID     = var.AWS_ACCESS_KEY_ID,
      SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY,
      DB_HOST           = var.DB_HOST,
      DB_NAME           = var.DB_NAME,
      DB_USER           = var.DB_USER,
      DB_PASS       = var.DB_PASS,
      DB_PORT           = var.DB_PORT,
      LOCAL_FOLDER      = var.LOCAL_FOLDER,
      SOURCE_EMAIL      = var.SOURCE_EMAIL
    }
  }
}