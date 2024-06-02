#-----------------------------------------------------------------------------------------------------------------------
# CloudWatch Log Group
#-----------------------------------------------------------------------------------------------------------------------
# CodeBuild用ロググループ
resource "aws_cloudwatch_log_group" "cloudflare_ipv4" {
  name              = local.codebuild_log_group_name
  skip_destroy      = false
  log_group_class   = "STANDARD"
  retention_in_days = local.codebuild_log_retention_in_days
}
