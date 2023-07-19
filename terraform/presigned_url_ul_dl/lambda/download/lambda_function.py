import json
import datetime
import botocore
import boto3
import os

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_PREFIX_NAME = os.environ["S3_PREFIX_NAME"]
DURATION_SECONDS = int(os.environ["DURATION_SECONDS"])

# S3クライアント
s3_client = boto3.client("s3")

def lambda_handler(event, context):
    
    # 戻り値の初期化
    return_obj = dict()
    return_obj["body"] = dict()
    
    # バケット名の設定
    return_obj["body"]["bucket"] = S3_BUCKET_NAME
    # フォルダー名の設定
    return_obj["body"]["prefix"] = S3_PREFIX_NAME
    # ファイル (オブジェクト) 一覧の初期化
    return_obj["body"]["contents"] = []
    
    # ファイル一覧情報の取得
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_PREFIX_NAME)
    
    for content in response["Contents"]:
    
        # ファイル情報の初期化
        object = dict()
        
        # ファイルサイズの取得
        size = content["Size"]
        if(size == 0):
          # ファイルサイズが 0 の場合、その後の処理をスキップ
          continue
        
        # ファイル名の取得と戻り値への設定
        key = content["Key"]
        object["name"] = key.replace(S3_PREFIX_NAME, "").replace("/", "")
        
        # ファイルサイズの戻り値への設定
        object["size"] = "{:,} Bytes".format(size)
        
        # ファイル更新日時の取得と戻り値への設定
        # 日本のタイムゾーン (JST)
        tz_jst = datetime.timezone(datetime.timedelta(hours=9))
        # 取得日時をJSTに変換
        dt_jst = content['LastModified'].astimezone(tz_jst)
        object["lastModified"] = dt_jst.strftime('%Y/%m/%d %H:%M:%S')
        
        # 署名付き URL の取得と戻り値への設定
        object["presignedUrl"] = s3_client.generate_presigned_url(
            ClientMethod = "get_object",
            Params = {"Bucket" : S3_BUCKET_NAME, "Key" : key},
            ExpiresIn = DURATION_SECONDS,
            HttpMethod = "GET"
        )
    
        # 取得した各情報の戻り値への設定
        return_obj["body"]["contents"].append(object)
  
    return_obj["statusCode"] = 200
    return_obj["body"] = json.dumps(return_obj["body"])
    
    return return_obj
