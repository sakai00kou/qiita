#!/bin/bash
#####################################################################
# CloudFlare用マネージドプレフィックスリスト更新スクリプト
#####################################################################
# -------------------------------------------------------------------
# 環境変数
# -------------------------------------------------------------------
# NO_CHANGE_FLAG      : 変更フラグ
# AWS_DEFAULT_REGION  : デフォルトリージョン
# OLD_LIST_FILE_FILE  : 古いIPアドレスリストファイル名
# NEW_LIST_FILE_FILE  : 新しいIPアドレスリストファイル名
# DELETE_LIST_FILE    : 削除IPアドレスリストファイル名
# ADD_LIST_FILE       : 追加IPアドレスリストファイル名
# PREFIX_LIST_ID_IPV4 : IPv4マネージドプレフィックスリストID
# PREFIX_LIST_ID_IPV6 : IPv6マネージドプレフィックスリストID
WORK_DIR=".tmp_cloudflare_update_ip"
NO_CHANGE_FLAG=0
AWS_DEFAULT_REGION="ap-northeast-1"
OLD_LIST_FILE="${WORK_DIR}/list_old"
NEW_LIST_FILE="${WORK_DIR}/list_new"
DELETE_LIST_FILE="${WORK_DIR}/delete_list"
ADD_LIST_FILE="${WORK_DIR}/add_list"
PREFIX_LIST_ID_IPV4="pl-xxxxxxxxxxxxxxxxx"
PREFIX_LIST_ID_IPV6="pl-yyyyyyyyyyyyyyyyy"

# -------------------------------------------------------------------
# エラー処理関数
# -------------------------------------------------------------------
function Err_handle()
{
	case $1 in
		1) MSGTXT="正しいプレフィックスIDが指定されているか確認してください。"
			echo "${MSGTXT}"
      # 作業用ファイル削除
      rm -rf ${WORK_DIR}
      exit 1 ;;
		2) MSGTXT="CloudFlareのIPアドレスリスト取得に失敗しました。"
			echo "${MSGTXT}"
      # 作業用ファイル削除
      rm -rf ${WORK_DIR}
      exit 1 ;;
		3) MSGTXT="マネージドプレフィックスリストの上限に達したか、実行コマンドに失敗しました。"
			echo "${MSGTXT}"
      # 作業用ファイル削除
      rm -rf ${WORK_DIR}
      exit 1 ;;
	esac
}

# -------------------------------------------------------------------
# マネージドプレフィックスリスト更新関数
# $1: マネージドプレフィックスリストID
# $2: ipv4 or ipv6
# -------------------------------------------------------------------
function IP_List_Update()
{
  # マネージドプレフィックスリストのエントリを取得
  aws ec2 get-managed-prefix-list-entries --prefix-list-id $1 | jq -r '.Entries[].Cidr' | sort > ${OLD_LIST_FILE}_$2

  # エラー処理
  if [ ${PIPESTATUS[0]} -ne 0 ]; then
    Err_handle 1
  fi

  # CloudFlareのIPアドレスリストを取得
  curl -s --request GET --url https://api.cloudflare.com/client/v4/ips --header 'Content-Type: application/json' | jq -r ".result.$2_cidrs[]" | sort > ${NEW_LIST_FILE}_$2
  # エラー処理
  if [ ${PIPESTATUS[1]} -ne 0 ]; then
    Err_handle 2
  fi
  # 比較用ファイル作成
  diff ${OLD_LIST_FILE}_$2 ${NEW_LIST_FILE}_$2 | awk '/^</ {print $2}' > ${DELETE_LIST_FILE}_$2
  diff ${OLD_LIST_FILE}_$2 ${NEW_LIST_FILE}_$2 | awk '/^>/ {print $2}' > ${ADD_LIST_FILE}_$2

  # マネージドプレフィックスリストの更新判定
  if [ ! -s ${DELETE_LIST_FILE}_$2 ] && [ ! -s ${ADD_LIST_FILE}_$2 ]; then
    NO_CHANGE_FLAG=1
  else
    # マネージドプレフィックスリストの現在のバージョン取得と削除＆追加用コマンド作成
    LIST_VERSION=$(aws ec2 describe-managed-prefix-lists --prefix-list-ids $1 | jq -r '.PrefixLists[].Version')
    DELETE_LIST_COMMAND="$(awk '{printf "Cidr=%s ", $1}' ${DELETE_LIST_FILE}_$2)"
    ADD_LIST_COMMAND="$(awk -v timestamp="$(date +'%Y-%m-%d')" '{printf "Cidr=%s,Description=Add_" timestamp "_CloudFlare ", $1}' ${ADD_LIST_FILE}_$2)"
    # マネージドプレフィックスリストへの追加＆削除がある場合
    if [ -s ${DELETE_LIST_FILE}_$2 ] && [ -s ${ADD_LIST_FILE}_$2 ]; then
      aws ec2 modify-managed-prefix-list \
        --prefix-list-id $1 \
        --remove-entries ${DELETE_LIST_COMMAND} \
        --add-entries ${ADD_LIST_COMMAND} \
        --current-version ${LIST_VERSION} 2>&1 > /dev/null
    # マネージドプレフィックスリストへの削除がある場合
    elif [ -s ${DELETE_LIST_FILE}_$2 ] && [ ! -s ${ADD_LIST_FILE}_$2 ]; then
      aws ec2 modify-managed-prefix-list \
        --prefix-list-id $1 \
        --remove-entries ${DELETE_LIST_COMMAND} \
        --current-version ${LIST_VERSION} 2>&1 > /dev/null
    # マネージドプレフィックスリストへの追加がある場合
    else
      aws ec2 modify-managed-prefix-list \
        --prefix-list-id $1 \
        --add-entries ${ADD_LIST_COMMAND} \
        --current-version ${LIST_VERSION} 2>&1 > /dev/null
    fi

    # エラー処理
    if [ $? -ne 0 ]; then
      Err_handle 3
    fi
  fi
}

# -------------------------------------------------------------------
# メイン処理
# -------------------------------------------------------------------
# 作業用ディレクトリ作成
mkdir ${WORK_DIR}

# IPv4マネージドプレフィックスリスト更新
IP_List_Update ${PREFIX_LIST_ID_IPV4} "ipv4"
NO_CHANGE_FLAG_IPV4=${NO_CHANGE_FLAG}

# IPv6マネージドプレフィックスリスト更新
IP_List_Update ${PREFIX_LIST_ID_IPV6} "ipv6"
NO_CHANGE_FLAG_IPV6=${NO_CHANGE_FLAG}

# 結果表示
if [ ${NO_CHANGE_FLAG_IPV4} -eq 1 ] && [ ${NO_CHANGE_FLAG_IPV6} -eq 1 ]; then
  echo "変更はありません。"
  rm -rf ${WORK_DIR}
else
  echo "--------------------"
  echo "削除リスト"
  echo "--------------------"
  echo "# IPv4"
  cat ${DELETE_LIST_FILE}_ipv4
  echo "# IPv6"
  cat ${DELETE_LIST_FILE}_ipv6
  echo ""
  echo "--------------------"
  echo "追加リスト"
  echo "--------------------"
  echo "# IPv4"
  cat ${ADD_LIST_FILE}_ipv4
  echo "# IPv6"
  cat ${ADD_LIST_FILE}_ipv6
  rm -rf ${WORK_DIR}
fi
