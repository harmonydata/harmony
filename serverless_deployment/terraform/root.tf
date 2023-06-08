# Show the results of running the data source. This is a map of environment
# variable names to their values.
data "external" "env" {
  program = ["${path.module}/env.sh"]
}

# Get the existing function details (created by SAM) so that we don't overwrite them

data "aws_lambda_function" "existing_matcher" {
    function_name = file("harmony_matcher.txt")
  
}

data "aws_lambda_function" "existing_file_processor" {
    function_name = file("harmony_file_processor.txt")
  
}

data "aws_lambda_function" "existing_pdf_parser" {
    function_name = file("harmony_pdf_parser.txt")
  
}

resource "aws_lambda_function" "harmony_matcher" {


  description   = "Call the Harmony matcher"
  filename      = "dummy.zip"
  function_name = file("harmony_matcher.txt")
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]
  vpc_config {
    subnet_ids         = [for s in aws_subnet.subnet : s.id]
    security_group_ids = [aws_security_group.efs.id]
  }
  tags = {
    "lambda:createdBy" = "SAM"
  }


  environment {
    variables = {
      VECTOR_API_KEY = data.external.env.result["HUGGING_FACE_API_KEY"]
    }
  }


  ######################
  # Elastic File System
  ######################

  file_system_config {
    # EFS file system access point ARN
    arn = aws_efs_access_point.lambda.arn

    # Local mount path inside the lambda function. Must start with '/mnt/'.
    local_mount_path = "/mnt/efs"
  }

  layers = ["arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python39:6"]

}



resource "aws_lambda_function" "harmony_file_processor" {
  description   = "File processor for text and Excel formats"
  image_uri = "${data.aws_lambda_function.existing_file_processor.image_uri}"
  package_type  = "Image"
  function_name = file("harmony_file_processor.txt")
  role          = aws_iam_role.lambda_role.arn
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]
  vpc_config {
    subnet_ids         = [for s in aws_subnet.subnet : s.id]
    security_group_ids = [aws_security_group.efs.id]


  }
  
  timeout = 15

  memory_size = 256

  tags = {
    "lambda:createdBy" = "SAM"
  }
  ######################
  # Elastic File System
  ######################

  file_system_config {
    # EFS file system access point ARN
    arn = aws_efs_access_point.lambda.arn

    # Local mount path inside the lambda function. Must start with '/mnt/'.
    local_mount_path = "/mnt/efs"
  }


}


resource "aws_lambda_function" "harmony_pdf_parser" {
  description   = "Wrapper for Tika (Java) which is for parsing PDFs"
  filename      = "dummy.zip"
  function_name = file("harmony_pdf_parser.txt")
  role          = aws_iam_role.lambda_role.arn
  handler       = "harmony.HandlerPDF"
  runtime       = "java11"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]
  memory_size   = 2048
  timeout       = 10

  tags = {
    "lambda:createdBy" = "SAM"
  }


}

