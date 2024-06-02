#-----------------------------------------------------------------------------------------------------------------------
# EventBridge Schedule
#-----------------------------------------------------------------------------------------------------------------------
# CloudflareグローバルIP更新CodeBuild実行用スケジュール
resource "aws_scheduler_schedule" "cloudflare_ipv4" {
  name                         = local.eb_schedule_name
  description                  = local.eb_schedule_description
  group_name                   = "default"
  schedule_expression_timezone = "Asia/Tokyo"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = local.eb_schedule_cron

  target {
    arn      = aws_codebuild_project.cloudflare_ipv4.arn
    role_arn = aws_iam_role.eb_schedule_role.arn
  }
}
