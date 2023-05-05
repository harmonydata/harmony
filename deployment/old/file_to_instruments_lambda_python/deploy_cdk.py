from aws_cdk import core, aws_sam as sam, aws_lambda

class AWSSDKPandasApp(core.Construct):
  def __init__(self, scope: core.Construct, id_: str):
    super.__init__(scope,id)

    aws_sdk_pandas_layer = sam.CfnApplication(
      self,
      "awssdkpandas-layer",
      location=sam.CfnApplication.ApplicationLocationProperty(
        application_id="arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python39:6",
        semantic_version="2.20.0",  # Get the latest version from https://serverlessrepo.aws.amazon.com/applications
      ),
    )

    aws_sdk_pandas_layer_arn = aws_sdk_pandas_layer.get_att("Outputs.WranglerLayer38Arn").to_string()
    aws_sdk_pandas_layer_version = aws_lambda.LayerVersion.from_layer_version_arn(self, "awssdkpandas-layer-version", aws_sdk_pandas_layer_arn)

    aws_lambda.Function(
      self,
      "awssdkpandas-function",
      runtime=aws_lambda.Runtime.PYTHON_3_8,
      function_name="harmony-process-file",
      code=aws_lambda.Code.from_asset("./src/awssdk-pandas-lambda"),
      handler='lambda_function.lambda_handler',
      layers=[aws_sdk_pandas_layer_version]
    )