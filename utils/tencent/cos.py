
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

from sts.sts import Sts

from saas_29.settings import SecretId, SecretKey

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def create_cos(region='ap-nanjing'):
    secret_id = SecretId      # 替换为用户的 secretId
    secret_key = SecretKey      # 替换为用户的 secretKey
    region = region    # 替换为用户的 Region
    token = None                # 使用临时密钥需要传入 Token，默认为空，可不填
    scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    # 2. 获取客户端对象
    client = CosS3Client(config)

    return client


def cos_acquire_sts(request):
    """前端获取临时凭证"""
    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': SecretId,
        # 固定密钥
        'secret_key': SecretKey,
        # 换成你的 bucket
        'bucket': request.tracer.project.bucket,
        # 换成 bucket 所在地区
        'region': 'ap-nanjing',
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        # 文件前缀
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            # 'name/cos:PutObject',
            # 'name/cos:PostObject',
            # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload'
            "*"
        ],

    }

    sts = Sts(config)
    res = sts.get_credential()
    return res


if __name__ == "__main__":
    client = create_cos()
    response = client.create_bucket(
        Bucket='user-id-8-user-mobile-1556124506551-test-1302000219',
        ACL='public-read'
    )