#-----------------------------------------------------------------------------------------------------------------------
# Cognito 環境変数
#-----------------------------------------------------------------------------------------------------------------------
# cognito_sms_external_id（Cognito SMS送信用の外部ID）は以下コマンドでUUID生成
# uuidgen | tr "[:upper:]" "[:lower:]"
locals {
  # Cognito設定
  cognito_user_pool_name             = "Cognito-UserPool"
  cognito_sms_external_id            = "2b5de06d-c134-438a-b755-697b94f786db"
  cognito_resource_server_name       = "Cognito-ResourceServer"
  cognito_resource_server_identifier = "Cognito-ResourceServer-Identifier"
  cognito_domain                     = "presigned-url-ul-dl"
  cognito_user_pool_client_name      = "Cognito-Client"
  cognito_sms_iam_role_name          = "cognito-sms-role"
  cognito_sms_iam_policy_name        = "cognito-sms-policy"
  # S3設定
  s3_presigned_url_ul_dl_bucket = "presigned-url-ul-dl-bucket"
  # Lambda設定
  lambda_upload_function_name   = "s3-upload-lambda"
  lambda_download_function_name = "s3-download-lambda"
  lambda_iam_role_name          = "s3-ul-dl-lambda-role"
  lambda_iam_policy_name        = "s3-ul-dl-lambda-policy"
  # API Gateway設定
  apigw_name                    = "s3-ul-dl-apigw"
  apigw_cognito_authorizer_name = "s3-ul-dl-authorizer"
  apigw_iam_role_name           = "s3-ul-dl-apigw-role"
}

# アカウントIDとリージョンを取得
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# タグに付与するロール名
variable "role" {
  default = "presigned-url-ul-dl"
}