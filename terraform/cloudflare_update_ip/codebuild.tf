#----------------------------------------------------------------------------------------------------------------------
# CloudflareグローバルIP更新用CodeBuildプロジェクト
#----------------------------------------------------------------------------------------------------------------------
resource "aws_codebuild_project" "cloudflare_ipv4" {
  name         = local.codebuild_proj_name
  service_role = aws_iam_role.codebuild_iam_role.arn

  source {
    type      = "NO_SOURCE"
    buildspec = file("source/buildspec.yml")
  }

  environment {
    # Docker in Dockerでdocker実行する場合はprivileged_modeをtrueにする
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = false

    #-------------------------------------------------------------------------------------------------------------------
    # CodeBuild用環境変数
    #-------------------------------------------------------------------------------------------------------------------
    # リージョン
    environment_variable {
      name  = "PREFIX_LIST_ID_IPV4"
      value = aws_ec2_managed_prefix_list.cloudflare_ipv4.id
    }
    environment_variable {
      name  = "PREFIX_LIST_ID_IPV6"
      value = aws_ec2_managed_prefix_list.cloudflare_ipv6.id
    }
  }

  artifacts {
    type = "NO_ARTIFACTS"
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.cloudflare_ipv4.name
      stream_name = local.codebuild_log_stream_name
    }
  }
}
