#-----------------------------------------------------------------------------------------------------------------------
# API Gateway API作成
#-----------------------------------------------------------------------------------------------------------------------
# APIの作成
resource "aws_api_gateway_rest_api" "ul_dl_apigw" {
  name        = local.apigw_name
  description = local.apigw_name
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway オーソライザー
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name            = local.apigw_cognito_authorizer_name
  rest_api_id     = aws_api_gateway_rest_api.ul_dl_apigw.id
  type            = "COGNITO_USER_POOLS"
  identity_source = "method.request.header.Authorization"
  provider_arns = [
    "${aws_cognito_user_pool.pool.arn}"
  ]
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway リソースパス
#-----------------------------------------------------------------------------------------------------------------------
# リソースパスの作成
# /web
resource "aws_api_gateway_resource" "ul_dl_web" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  parent_id   = aws_api_gateway_rest_api.ul_dl_apigw.root_resource_id
  path_part   = "web"
}

resource "aws_api_gateway_resource" "ul_dl_web_proxy" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  parent_id   = aws_api_gateway_resource.ul_dl_web.id
  path_part   = "{proxy+}"
}

# /api
resource "aws_api_gateway_resource" "ul_dl_api" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  parent_id   = aws_api_gateway_rest_api.ul_dl_apigw.root_resource_id
  path_part   = "api"
}

# /api/upload
resource "aws_api_gateway_resource" "ul_dl_api_upload" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  parent_id   = aws_api_gateway_resource.ul_dl_api.id
  path_part   = "upload"
}

# /api/download
resource "aws_api_gateway_resource" "ul_dl_api_download" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  parent_id   = aws_api_gateway_resource.ul_dl_api.id
  path_part   = "download"
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway /api/upload/GET メソッド
#-----------------------------------------------------------------------------------------------------------------------
# /api/upload/GET
# メソッドリクエスト
resource "aws_api_gateway_method" "ul_dl_api_upload_get" {
  rest_api_id   = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id   = aws_api_gateway_resource.ul_dl_api_upload.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# 統合リクエスト
resource "aws_api_gateway_integration" "ul_dl_api_upload_get" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_api_upload.id
  http_method = aws_api_gateway_method.ul_dl_api_upload_get.http_method
  # Lambdaの場合、POSTを指定する必要がある。
  content_handling        = "CONVERT_TO_TEXT"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_lambda.invoke_arn
}

# メソッドレスポンス
resource "aws_api_gateway_method_response" "ul_dl_api_upload_get" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_api_upload.id
  http_method = aws_api_gateway_method.ul_dl_api_upload_get.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {}
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway /api/download/GET メソッド
#-----------------------------------------------------------------------------------------------------------------------
# /api/download/GET
# メソッドリクエスト
resource "aws_api_gateway_method" "ul_dl_api_download_get" {
  rest_api_id   = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id   = aws_api_gateway_resource.ul_dl_api_download.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# 統合リクエスト
resource "aws_api_gateway_integration" "ul_dl_api_download_get" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_api_download.id
  http_method = aws_api_gateway_method.ul_dl_api_download_get.http_method
  # Lambdaの場合、POSTを指定する必要がある。
  content_handling        = "CONVERT_TO_TEXT"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.download_lambda.invoke_arn
}

# メソッドレスポンス
resource "aws_api_gateway_method_response" "ul_dl_api_download_get" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_api_download.id
  http_method = aws_api_gateway_method.ul_dl_api_download_get.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {}
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway /web/{proxy+}/GET メソッド
#-----------------------------------------------------------------------------------------------------------------------
# /web/{proxy+}/GET
# メソッドリクエスト
resource "aws_api_gateway_method" "ul_dl_web_proxy_get" {
  rest_api_id   = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id   = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.proxy" = true
  }
}

# 統合リクエスト
resource "aws_api_gateway_integration" "ul_dl_web_proxy" {
  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  # Lambdaの場合、POSTを指定する必要がある。
  integration_http_method = "GET"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.name}:s3:path/${aws_s3_bucket.presigned_url_ul_dl.bucket}/contents/{proxy}"
  cache_key_parameters = [
    "method.request.path.proxy",
  ]

  credentials          = aws_iam_role.apigw_role.arn
  passthrough_behavior = "WHEN_NO_MATCH"
  timeout_milliseconds = 29000
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# 統合レスポンス
resource "aws_api_gateway_integration_response" "ul_dl_web_proxy_200" {
  depends_on = [aws_api_gateway_method_response.ul_dl_web_proxy_200]

  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Content-Length" = "integration.response.header.Content-Length"
    "method.response.header.Content-Type"   = "integration.response.header.Content-Type"
    "method.response.header.Timestamp"      = "integration.response.header.Date"
  }
}

resource "aws_api_gateway_integration_response" "ul_dl_web_proxy_400" {
  depends_on = [aws_api_gateway_method_response.ul_dl_web_proxy_400]

  rest_api_id       = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id       = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method       = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  status_code       = "400"
  selection_pattern = "4\\d{2}"
}

resource "aws_api_gateway_integration_response" "ul_dl_web_proxy_500" {
  depends_on = [aws_api_gateway_method_response.ul_dl_web_proxy_500]

  rest_api_id       = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id       = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method       = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  status_code       = "500"
  selection_pattern = "5\\d{2}"
}

# メソッドレスポンス
resource "aws_api_gateway_method_response" "ul_dl_web_proxy_200" {
  depends_on = [aws_api_gateway_integration.ul_dl_web_proxy]

  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Content-Length" = false
    "method.response.header.Content-Type"   = false
    "method.response.header.Timestamp"      = false
  }
}

resource "aws_api_gateway_method_response" "ul_dl_web_proxy_400" {
  depends_on = [aws_api_gateway_integration.ul_dl_web_proxy]

  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  status_code = "400"
}

resource "aws_api_gateway_method_response" "ul_dl_web_proxy_500" {
  depends_on = [aws_api_gateway_integration.ul_dl_web_proxy]

  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  resource_id = aws_api_gateway_resource.ul_dl_web_proxy.id
  http_method = aws_api_gateway_method.ul_dl_web_proxy_get.http_method
  status_code = "500"
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway デプロイ
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_api_gateway_deployment" "ul_dl_apigw" {
  depends_on = [
    aws_api_gateway_method.ul_dl_api_upload_get,
    aws_api_gateway_integration.ul_dl_api_upload_get,
    aws_api_gateway_method_response.ul_dl_api_upload_get,
    aws_api_gateway_method.ul_dl_api_download_get,
    aws_api_gateway_integration.ul_dl_api_download_get,
    aws_api_gateway_method_response.ul_dl_api_download_get,
    aws_api_gateway_method.ul_dl_web_proxy_get,
    aws_api_gateway_integration.ul_dl_web_proxy,
    aws_api_gateway_integration_response.ul_dl_web_proxy_200,
    aws_api_gateway_integration_response.ul_dl_web_proxy_400,
    aws_api_gateway_integration_response.ul_dl_web_proxy_500,
    aws_api_gateway_method_response.ul_dl_web_proxy_200,
    aws_api_gateway_method_response.ul_dl_web_proxy_400,
    aws_api_gateway_method_response.ul_dl_web_proxy_500,
  ]

  rest_api_id = aws_api_gateway_rest_api.ul_dl_apigw.id
  stage_name  = "dev"
  triggers = {
    # Lambdaの更新でデプロイする
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.ul_dl_apigw))
  }
}

# エントランスページのURLを出力
output "Entrance_Page_URL" {
  value = "${aws_api_gateway_deployment.ul_dl_apigw.invoke_url}/web/entrance.html"
}