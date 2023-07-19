#-----------------------------------------------------------------------------------------------------------------------
# アップロード・ダウンロードファイル格納用S3バケットの作成
#-----------------------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "presigned_url_ul_dl" {
  bucket = local.s3_presigned_url_ul_dl_bucket

  tags = {
    Name = local.s3_presigned_url_ul_dl_bucket
  }
}

# バージョニングの設定
resource "aws_s3_bucket_versioning" "presigned_url_ul_dl" {
  bucket = aws_s3_bucket.presigned_url_ul_dl.id
  versioning_configuration {
    status = "Disabled"
  }
}

# サーバー側の暗号化
resource "aws_s3_bucket_server_side_encryption_configuration" "presigned_url_ul_dl" {
  bucket = aws_s3_bucket.presigned_url_ul_dl.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ブロックパブリックアクセスの設定
resource "aws_s3_bucket_public_access_block" "bucket" {
  bucket = local.s3_presigned_url_ul_dl_bucket

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# バケット所有者の設定（ACL）
resource "aws_s3_bucket_ownership_controls" "bucket" {
  depends_on = [aws_s3_bucket.presigned_url_ul_dl]
  bucket     = local.s3_presigned_url_ul_dl_bucket

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# 静的ウェブサイトホスティングの設定
resource "aws_s3_bucket_website_configuration" "bucket" {
  bucket = local.s3_presigned_url_ul_dl_bucket

  index_document {
    suffix = "index.html"
  }
}

# CORSの設定
resource "aws_s3_bucket_cors_configuration" "bucket" {
  bucket = local.s3_presigned_url_ul_dl_bucket

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST"]
    allowed_origins = ["https://${aws_api_gateway_rest_api.ul_dl_apigw.id}.execute-api.${data.aws_region.current.name}.amazonaws.com"]
    expose_headers  = []
    max_age_seconds = 3000
  }
}

# バケットポリシーの設定
resource "aws_s3_bucket_policy" "bucket" {
  bucket = local.s3_presigned_url_ul_dl_bucket
  policy = data.aws_iam_policy_document.s3_bucket_policy.json
}

data "aws_iam_policy_document" "s3_bucket_policy" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.presigned_url_ul_dl.arn}/*",
    ]

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values = [
        "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.ul_dl_apigw.id}/*/GET/",
      ]
    }
  }
}