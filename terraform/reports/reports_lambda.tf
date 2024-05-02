resource "aws_iam_role" "archive-lambda-role" {
  name               = "c10-railway-archive-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda-role-policy.json
}

data "aws_ecr_repository" "archive-lambda-ecr-repo" {
  name = "c10-railway-archive"
}

data "aws_ecr_image" "archive-lambda-image" {
  repository_name = data.aws_ecr_repository.archive-lambda-ecr-repo.name
  image_tag       = "latest"
}

resource "aws_lambda_function" "archive-lambda" {
  role          = aws_iam_role.archive-lambda-role.arn
  function_name = "c10-railway-archive-lambda-terraform"
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.archive-lambda-image.image_uri
  memory_size   = 256
  timeout       = 600
  environment {
    variables = {
      ACCESS_KEY_ID     = var.AWS_ACCESS_KEY_ID,
      SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY,
      DB_HOST           = var.DB_HOST,
      DB_NAME           = var.DB_NAME,
      DB_USER           = var.DB_USER,
      DB_PASSWORD       = var.DB_PASS,
      DB_PORT           = var.DB_PORT,
      LOCAL_FOLDER      = var.LOCAL_FOLDER,
      SOURCE_EMAIL      = var.SOURCE_EMAIL
    }
  }
}