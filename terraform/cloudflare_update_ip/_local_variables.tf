#----------------------------------------------------------------------------------------------------------------------
# CloudflareグローバルIP更新処理用ローカル変数
#----------------------------------------------------------------------------------------------------------------------
locals {
  # マネージドプレフィックスリスト用変数
  mng_prefix_list_ipv4_name        = "cloudflare.global.ipv4.ips"
  mng_prefix_list_ipv6_name        = "cloudflare.global.ipv6.ips"
  mng_prefix_list_max_entries_ipv4 = 20
  mng_prefix_list_max_entries_ipv6 = 10

  # CodeBuild用変数
  codebuild_proj_name             = "cloudflare-update-ip-proj"
  codebuild_log_group_name        = "/codebuild/cloudflare-update-ip-logs"
  codebuild_log_retention_in_days = 30
  codebuild_log_stream_name       = "cloudflare-update-ip-stream"
  codebuild_iam_role_name         = "cloudflare-update-ip-codebuild-role"
  codebuild_iam_policy_name       = "cloudflare-update-ip-codebuild-policy"

  # EventBridgeスケジュール用変数
  eb_schedule_name            = "cloudflare-update-ip-schedule"
  eb_schedule_description     = "cloudflare-update-ip-schedule"
  eb_schedule_cron            = "cron(0 1 * * ? *)"
  eb_schedule_iam_role_name   = "cloudflare-update-ip-eb-role"
  eb_schedule_iam_policy_name = "cloudflare-update-ip-eb-policy"
}