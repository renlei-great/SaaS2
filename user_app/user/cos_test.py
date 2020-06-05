# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
from saas_29 import settings

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = settings.SecretId      # 替换为用户的 secretId
secret_key = settings.SecretKey      # 替换为用户的 secretKey
region = 'ap-nanjing'     # 替换为用户的 Region
token = None                # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
# 2. 获取客户端对象
client = CosS3Client(config)
# 参照下文的描述。或者参照 Demo 程序，详见 https://github.com/tencentyun/cos-python-sdk-v5/blob/master/qcloud_cos/demo.py

# with open('1.jpg', 'rb') as fp:
#     response = client.put_object(
#         Bucket='examplebucket-1250000000',
#         Body=fp,
#         Key='picture.jpg',
#         StorageClass='STANDARD',
#         EnableMD5=False
#     )


response = client.upload_file(
    Bucket='saas-pre-1302000219',
    LocalFilePath='1.jpg',
    Key='221.jpg',
    PartSize=1,
    MAXThread=10,
    EnableMD5=False
)

print(response)