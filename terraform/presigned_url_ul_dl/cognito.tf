#-----------------------------------------------------------------------------------------------------------------------
# Cognito ユーザプール
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_cognito_user_pool" "pool" {
  name = local.cognito_user_pool_name

  # 削除保護
  deletion_protection = "INACTIVE"

  # Cognitoユーザプールのサインインオプション
  auto_verified_attributes = [
    "email",
  ]

  # パスワードポリシー
  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  # 多要素認証
  mfa_configuration = "OPTIONAL"
  sms_configuration {
    external_id    = local.cognito_sms_external_id
    sns_caller_arn = aws_iam_role.cognito_sms_role.arn
    sns_region     = data.aws_region.current.name
  }
  software_token_mfa_configuration {
    enabled = false
  }

  # ユーザアカウントの復旧
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # セルフサービスのサインアップ
  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  # 属性検証とユーザーアカウントの確認
  username_attributes = [
    "email",
  ]

  # 属性変更の確認
  user_attribute_update_settings {
    attributes_require_verification_before_update = [
      "email",
    ]
  }

  # 必須の属性
  schema {
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = false
    name                     = "email"
    required                 = true

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  # Eメール
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }
}

#-----------------------------------------------------------------------------------------------------------------------
# Cognito リソースサーバ
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_cognito_resource_server" "resource" {
  name         = local.cognito_resource_server_name
  identifier   = local.cognito_resource_server_identifier
  user_pool_id = aws_cognito_user_pool.pool.id
}

#-----------------------------------------------------------------------------------------------------------------------
# Cognito ドメイン
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_cognito_user_pool_domain" "cognito_domain" {
  domain       = local.cognito_domain
  user_pool_id = aws_cognito_user_pool.pool.id
}

#-----------------------------------------------------------------------------------------------------------------------
# Cognito アプリケーションクライアント
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_cognito_user_pool_client" "client" {
  name         = local.cognito_user_pool_client_name
  user_pool_id = aws_cognito_user_pool.pool.id
  # 認証フロー
  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]
  # 単位設定
  token_validity_units {
    refresh_token = "days"
    access_token  = "minutes"
    id_token      = "minutes"
  }
  # 有効期限
  auth_session_validity  = 3
  refresh_token_validity = 30
  access_token_validity  = 60
  id_token_validity      = 60
  # 高度な認証設定
  enable_token_revocation       = true
  prevent_user_existence_errors = "ENABLED"

  # ホストされたUI
  callback_urls = [
    "https://${aws_api_gateway_rest_api.ul_dl_apigw.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_deployment.ul_dl_apigw.stage_name}/web/upload.html",
    "https://${aws_api_gateway_rest_api.ul_dl_apigw.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_deployment.ul_dl_apigw.stage_name}/web/entrance.html",
    "https://${aws_api_gateway_rest_api.ul_dl_apigw.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_deployment.ul_dl_apigw.stage_name}/web/download.html",
  ]
  logout_urls = [
    "https://${aws_api_gateway_rest_api.ul_dl_apigw.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_deployment.ul_dl_apigw.stage_name}/web/entrance.html",
  ]
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid", "phone"]
}