import json
import boto3
from botocore.client import Config

import os

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_PREFIX_NAME = os.environ["S3_PREFIX_NAME"]
DURATION_SECONDS = int(os.environ["DURATION_SECONDS"])

s3_client = boto3.client("s3", config=Config(signature_version="s3v4")) 


def lambda_handler(event, context):

    # 戻り値の初期化
    return_obj = dict()
    return_obj["body"] = dict()
    
    # バケット名の設定
    return_obj["body"]["bucket"] = S3_BUCKET_NAME
    # フォルダー名の設定
    return_obj["body"]["prefix"] = S3_PREFIX_NAME

    target_info = s3_client.generate_presigned_post(S3_BUCKET_NAME,
                                                    S3_PREFIX_NAME + "${filename}", 
                                                    Fields=None,
                                                    Conditions=None,
                                                    ExpiresIn=DURATION_SECONDS)
    
    # 取得した各情報の戻り値への設定
    return_obj["body"]["contents"] = target_info
    
    return_obj["statusCode"] = 200
    return_obj["body"] = json.dumps(return_obj["body"])

    return return_obj
