# Entry point for Harmony calling Hugging Face to vectorise a text

How to deploy to AWS Lambda:

```
pip install -r requirements.txt
cdk bootstrap
cdk synth
cdk deploy
```

If you get an error and need to start again, you can do

```
cdk destroy
```

If you still get stuck, you may have to delete some resources e.g. buckets from AWS using the CLI. A useful tool is AWS Nuke https://github.com/rebuy-de/aws-nuke.

Based on "Zero administration inference with AWS Lambda for HuggingFace" https://github.com/aws-samples/zero-administration-inference-with-aws-lambda-for-hugging-face

![Architecture diagram](serverless-hugging-face.png)
In this architectural diagram:
1.  Serverless inference is achieved by using Lambda functions that are
    based on container image
2.  The container image is stored in an [Amazon Elastic Container
    Registry](https://aws.amazon.com/ecr/) (ECR) repository within your
    account
3.  Pre-trained models are automatically downloaded from Hugging Face
    the first time the function is invoked
4.  Pre-trained models are cached within Amazon Elastic File System
    storage in order to improve inference latency

## Prerequisites
The following is required to deploy this:
-   [AWS CDK v2](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
-   [Python](https://www.python.org/) 3.6+
-   [A virtual env](https://docs.python.org/3/library/venv.html#module-venv) (optional)

## Understanding the code structure
The code is organized using the following structure:
```bash
├── inference
│   ├── Dockerfile
│   └── vectorisation.py
├── app.py
└── ...
```

For each Python script in the inference directory, the CDK generates a
Lambda function backed by a container image and a Python inference
script.

## Cleaning up
After you are finished experimenting with this project, run ```cdk destroy``` to remove all of the associated infrastructure.

## Links
- [https://github.com/aws-samples/zero-administration-inference-with-aws-lambda-for-hugging-face](https://github.com/aws-samples/zero-administration-inference-with-aws-lambda-for-hugging-face)
- [:hugs:](https://huggingface.co)
- [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)
- [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Amazon Elastic File System](https://aws.amazon.com/efs/)
