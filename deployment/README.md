# Deployment scripts

Here are the scripts for deploying various parts of Harmony to AWS.

The deployment is also set up as Github Actions.

If deploying manually, you should run them in this order:

1. `pdf_processor_tika_lambda_java`

2. `file_processor_docker_lambda`

3. `matcher_lambda`

By default we use the HuggingFace models API to run the transformer model, for cost effectiveness. However, an optional AWS Lambda function is also in this folder.

`optional_transformer_llm_huggingface_lambda`

You should also create an Express Step Function using the file `step_function_express_state_machine.json`.

And an API Gateway instance pointing to the step function and the `matcher_lambda` deployment.  

## List of Resources Needed for Deployment

1. HuggingFace API
2. Lambda function - matcher
3. Lambda function - PDF parser Tika
4. Lambda function - Generic file parser
5. Express Step function to orchestrate two file parsers (#3 and #4) - see JSON file in this directory
6. API Gateway
7. EFS File system - `harmonyefs` with access point
8. VPC