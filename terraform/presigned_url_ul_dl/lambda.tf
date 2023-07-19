#-----------------------------------------------------------------------------------------------------------------------
# アップロード用Lambda
#-----------------------------------------------------------------------------------------------------------------------
# Lambda関数のアーカイブファイル作成
data "archive_file" "upload_zip" {
  type        = "zip"
  source_dir  = "lambda/upload"
  output_path = "lambda/archive/lambda_upload.zip"
}

# アップロード用Lambda関数の作成
resource "aws_lambda_function" "upload_lambda" {
  filename      = data.archive_file.upload_zip.output_path
  function_name = local.lambda_upload_function_name
  role          = aws_iam_role.ul_dl_lambda_role.arn
  # ランタイム設定
  runtime          = "python3.10"
  handler          = "lambda_function.lambda_handler"
  architectures    = ["x86_64"]
  timeout          = 3
  source_code_hash = data.archive_file.upload_zip.output_base64sha256

  # 環境変数
  environment {
    variables = {
      DURATION_SECONDS = "3600"
      S3_BUCKET_NAME   = aws_s3_bucket.presigned_url_ul_dl.id
      S3_PREFIX_NAME   = "upload/"
    }
  }
}

# トリガー設定用Lambda Permissionの作成
resource "aws_lambda_permission" "upload_lambda" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upload_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ul_dl_apigw.execution_arn}/*/GET/api/upload"
}

#-----------------------------------------------------------------------------------------------------------------------
# ダウンロード用Lambda
#-----------------------------------------------------------------------------------------------------------------------
# Lambda関数のアーカイブファイル作成
data "archive_file" "download_zip" {
  type        = "zip"
  source_dir  = "lambda/download"
  output_path = "lambda/archive/lambda_download.zip"
}

# ダウンロード用Lambda関数の作成
resource "aws_lambda_function" "download_lambda" {
  filename      = data.archive_file.download_zip.output_path
  function_name = local.lambda_download_function_name
  role          = aws_iam_role.ul_dl_lambda_role.arn
  # ランタイム設定
  runtime          = "python3.10"
  handler          = "lambda_function.lambda_handler"
  architectures    = ["x86_64"]
  timeout          = 3
  source_code_hash = data.archive_file.download_zip.output_base64sha256

  # 環境変数
  environment {
    variables = {
      DURATION_SECONDS = "3600"
      S3_BUCKET_NAME   = aws_s3_bucket.presigned_url_ul_dl.id
      S3_PREFIX_NAME   = "download/"
    }
  }
}

# トリガー設定用Lambda Permissionの作成
resource "aws_lambda_permission" "download_lambda" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.download_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ul_dl_apigw.execution_arn}/*/GET/api/download"
}