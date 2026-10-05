output "api_url" {
  value = aws_apigatewayv2_api.api.api_endpoint
}

output "function_name" {
  value = aws_lambda_function.api.function_name
}

output "log_group" {
  value = aws_cloudwatch_log_group.lambda.name
}
