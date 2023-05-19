resource "aws_sfn_state_machine" "sfn_state_machine" {
  type     = "EXPRESS"
  name     = "HarmonyExpressStateMachine"
  role_arn = aws_iam_role.lambda_role.arn

  definition = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "TriageFileType",
  "States": {
    "TriageFileType": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$[0].file_type",
          "StringEquals": "pdf",
          "Next": "ProcessPdf"
        }
      ],
      "Default": "ProcessTextOrExcel"
    },
    "ProcessPdf": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$",
      "ResultPath": "$",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "${aws_lambda_function.harmony_pdf_parser.arn}"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2
        }
      ],
       "Next": "ProcessTextOrExcel"
    },
    "ProcessTextOrExcel": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "${aws_lambda_function.harmony_file_processor.arn}"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2
        }
      ],
      "End": true
    }
  }
}
EOF
}
