resource "aws_iam_role" "lambda_role" {
  name               = "Harmony_Test_Lambda_Function_Role"
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   },
   {
      "Effect": "Allow",
      "Principal": {
        "Service": "states.eu-west-2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
 ]
}
EOF
}



resource "aws_iam_policy" "iam_policy_for_lambda" {

  name        = "aws_iam_policy_for_terraform_aws_lambda_role"
  path        = "/"
  description = "AWS IAM Policy for managing aws lambda role"
  policy      = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": [
       "logs:CreateLogGroup",
       "logs:CreateLogStream",
       "logs:PutLogEvents"
     ],
     "Resource": "arn:aws:logs:*:*:*",
     "Effect": "Allow"
   },
   {
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
 ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.iam_policy_for_lambda.arn
}

resource "aws_iam_role_policy_attachment" "attach_basic_execution_policy_to_iam_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "attach_xray_policy_to_iam_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "attach_readonly_to_iam_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_ReadOnlyAccess"
}


resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "StateMachineToLambdaRole" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::017696512810:policy/service-role/LambdaInvokeScopedAccessPolicy-71b61bcd-2a6a-41de-b185-8af8a9e55675"
}

resource "aws_iam_role_policy_attachment" "StateMachineCloudWatch" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::017696512810:policy/service-role/CloudWatchLogsDeliveryFullAccessPolicy-e0e3abcb-2fc8-419e-9afd-20b9cd409875"
}

resource "aws_iam_role_policy_attachment" "StateMachineToXRay" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::017696512810:policy/service-role/XRayAccessPolicy-9f77b45c-fd34-4b88-8ad6-bcff25924c60"
}

data "archive_file" "dummy" {
  type        = "zip"
  output_path = "dummy.zip"
  source {
    content  = "hello"
    filename = "dummy.txt"
  }
}


/*
resource "aws_lambda_function" "harmony_matcher" {
filename                       = "${data.archive_file.dummy.output_path}"
function_name                  = "harmony-matcher"
role                           = aws_iam_role.lambda_role.arn
handler                        = "lambda_function.lambda_handler"
runtime                        = "python3.9"
depends_on                     = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role, aws_efs_mount_target.efs_mt]
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
*/
