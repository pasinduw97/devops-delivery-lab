locals {
  name          = "releaseops-lab"
  alarm_actions = var.alarm_topic_arn == "" ? [] : [var.alarm_topic_arn]
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "gateway" {
  name              = "/releaseops/api"
  retention_in_days = 7
}

resource "aws_iam_role" "lambda" {
  name = "${local.name}-runtime"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "logs" {
  name = "write-own-logs"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.lambda.arn}:*"
    }]
  })
}

resource "aws_lambda_function" "api" {
  function_name                  = local.name
  role                           = aws_iam_role.lambda.arn
  runtime                        = "python3.13"
  handler                        = "app.service.lambda_handler"
  filename                       = "${path.module}/../build/lambda.zip"
  source_code_hash               = filebase64sha256("${path.module}/../build/lambda.zip")
  architectures                  = ["arm64"]
  memory_size                    = 128
  timeout                        = 5
  reserved_concurrent_executions = 2
  environment {
    variables = { APP_VERSION = var.app_version }
  }
  depends_on = [aws_iam_role_policy.logs]
}

resource "aws_apigatewayv2_api" "api" {
  name          = local.name
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "all" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
  default_route_settings {
    throttling_burst_limit   = 5
    throttling_rate_limit    = 2
    detailed_metrics_enabled = true
  }
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.gateway.arn
    format = jsonencode({
      request_id = "$context.requestId"
      status     = "$context.status"
      latency_ms = "$context.responseLatency"
    })
  }
}

resource "aws_lambda_permission" "gateway" {
  statement_id  = "AllowGatewayInvocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_cloudwatch_metric_alarm" "errors" {
  alarm_name          = "${local.name}-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  dimensions          = { FunctionName = aws_lambda_function.api.function_name }
  alarm_actions       = local.alarm_actions
}

resource "aws_cloudwatch_metric_alarm" "gateway_errors" {
  alarm_name          = "${local.name}-gateway-5xx"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "5xx"
  namespace           = "AWS/ApiGateway"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  dimensions          = { ApiId = aws_apigatewayv2_api.api.id }
  alarm_actions       = local.alarm_actions
}
