
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
from saas_29 import settings

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def create_cos(region='ap-nanjing'):
    secret_id = settings.SecretId      # 替换为用户的 secretId
    secret_key = settings.SecretKey      # 替换为用户的 secretKey
    region = region    # 替换为用户的 Region
    token = None                # 使用临时密钥需要传入 Token，默认为空，可不填
    scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    # 2. 获取客户端对象
    client = CosS3Client(config)

    return client


if __name__ == "__main__":
    client = create_cos()
    response = client.create_bucket(
        Bucket='user-id-8-user-mobile-15561245051-test-1302000219',
        ACL='public-read'
    )