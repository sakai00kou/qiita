#-----------------------------------------------------------------------------------------------------------------------
# アップロード・ダウンロードコンテンツ用ファイル
#-----------------------------------------------------------------------------------------------------------------------
# S3バケットに各ディレクトリを作成する。
resource "aws_s3_object" "make_directory" {
  for_each = toset([
    "contents",
    "upload",
    "download",
  ])

  bucket = aws_s3_bucket.presigned_url_ul_dl.bucket
  key    = "${each.key}/"
}

# "aws_s3_object"でファイルを配置した際に"Content-Type"が"binary/octet-stream"になることの対処。
module "presigned_ul_dl_files" {
  source   = "hashicorp/dir/template"
  base_dir = "./file"

  # テンプレートファイル（env-vals.js）の変数を定義する。
  template_vars = {
    userpool_domain    = local.cognito_domain
    userpool_region    = data.aws_region.current.name
    userpool_client_id = aws_cognito_user_pool_client.client.id
    execute_api_stage  = aws_api_gateway_deployment.ul_dl_apigw.stage_name
  }
}

# 各ファイルをS3バケットの/contentsに配置する。
resource "aws_s3_object" "send_file" {
  for_each = module.presigned_ul_dl_files.files

  bucket       = aws_s3_bucket.presigned_url_ul_dl.bucket
  key          = "contents/${each.key}"
  source       = each.value.source_path
  content      = each.value.content
  content_type = each.value.content_type
  etag         = each.value.digests.md5
}