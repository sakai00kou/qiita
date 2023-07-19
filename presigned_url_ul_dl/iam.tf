#-----------------------------------------------------------------------------------------------------------------------
# 署名付きURL Upload/Download Lambda用IAMロール
#-----------------------------------------------------------------------------------------------------------------------
# Assume Role
data "aws_iam_policy_document" "ul_dl_lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      identifiers = [
        "lambda.amazonaws.com",
      ]
      type = "Service"
    }
    actions = [
      "sts:AssumeRole",
    ]
  }
}

# IAM Role
resource "aws_iam_role" "ul_dl_lambda_role" {
  name               = local.lambda_iam_role_name
  assume_role_policy = data.aws_iam_policy_document.ul_dl_lambda_assume_role.json
  description        = local.lambda_iam_role_name
}

# IAM Policy
data "aws_iam_policy_document" "ul_dl_lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.presigned_url_ul_dl.id}",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.presigned_url_ul_dl.id}/*",
    ]
  }
}

resource "aws_iam_policy" "ul_dl_lambda_policy" {
  name        = local.lambda_iam_policy_name
  path        = "/"
  description = local.lambda_iam_policy_name
  policy      = data.aws_iam_policy_document.ul_dl_lambda_policy.json
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "ul_dl_lambda_role" {
  for_each = {
    ul_dl_lambda = aws_iam_policy.ul_dl_lambda_policy.arn
  }
  role       = aws_iam_role.ul_dl_lambda_role.name
  policy_arn = each.value
}

#-----------------------------------------------------------------------------------------------------------------------
# API Gateway用IAMロール
#-----------------------------------------------------------------------------------------------------------------------
# Assume Role
data "aws_iam_policy_document" "apigw_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

# IAM Role
resource "aws_iam_role" "apigw_role" {
  name               = local.apigw_iam_role_name
  assume_role_policy = data.aws_iam_policy_document.apigw_assume_role.json
  description        = local.apigw_iam_role_name
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "apigw_s3fullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.apigw_role.name
}

resource "aws_iam_role_policy_attachment" "apigw_cwlogs" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  role       = aws_iam_role.apigw_role.name
}

#-----------------------------------------------------------------------------------------------------------------------
# Cognito SMSメッセージ送信用IAMロール
#-----------------------------------------------------------------------------------------------------------------------
# Assume Role
data "aws_iam_policy_document" "cognito_sms_assume_role" {
  statement {
    effect = "Allow"
    principals {
      identifiers = [
        "cognito-idp.amazonaws.com",
      ]
      type = "Service"
    }
    actions = [
      "sts:AssumeRole",
    ]
    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values = [
        "${local.cognito_sms_external_id}",
      ]
    }
  }
}

# IAM Role
resource "aws_iam_role" "cognito_sms_role" {
  name               = local.cognito_sms_iam_role_name
  assume_role_policy = data.aws_iam_policy_document.cognito_sms_assume_role.json
  description        = local.cognito_sms_iam_role_name
}

# IAM Policy
data "aws_iam_policy_document" "cognito_sms_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sns:publish",
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "cognito_sms_policy" {
  name        = local.cognito_sms_iam_policy_name
  path        = "/"
  description = local.cognito_sms_iam_policy_name
  policy      = data.aws_iam_policy_document.cognito_sms_policy.json
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "cognito_sms_role" {
  for_each = {
    cognito_sms = aws_iam_policy.cognito_sms_policy.arn
  }
  role       = aws_iam_role.cognito_sms_role.name
  policy_arn = each.value
}