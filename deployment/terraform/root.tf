resource "aws_lambda_function" "harmony_matcher" {

  filename      = data.archive_file.dummy.output_path
  function_name = "harmony-matcher"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]
  vpc_config {
    subnet_ids         = [for s in aws_subnet.subnet : s.id]
    security_group_ids = [aws_security_group.efs.id]
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

resource "aws_lambda_function" "harmony_file_processor" {

  filename      = data.archive_file.dummy.output_path
  function_name = "harmony-file-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]
  vpc_config {
    subnet_ids         = [for s in aws_subnet.subnet : s.id]
    security_group_ids = [aws_security_group.efs.id]


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


  filename      = data.archive_file.dummy.output_path
  function_name = "harmony-pdf-parser"
  role          = aws_iam_role.lambda_role.arn
  handler       = "harmony.HandlerPDF"
  runtime       = "java11"
  depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]



}
