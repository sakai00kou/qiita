#----------------------------------------------------------------------------------------------------------------------
# CloudflareグローバルIP登録用マネージドプレフィックスリスト
#----------------------------------------------------------------------------------------------------------------------
# IPv4用マネージドプレフィックスリスト
resource "aws_ec2_managed_prefix_list" "cloudflare_ipv4" {
  name           = local.mng_prefix_list_ipv4_name
  address_family = "IPv4"
  max_entries    = local.mng_prefix_list_max_entries_ipv4

  # CodeBuildで更新するため、entryは無視する
}

# IPv6用マネージドプレフィックスリスト
resource "aws_ec2_managed_prefix_list" "cloudflare_ipv6" {
  name           = local.mng_prefix_list_ipv6_name
  address_family = "IPv6"
  max_entries    = local.mng_prefix_list_max_entries_ipv6

  # CodeBuildで更新するため、entryは無視する
}
