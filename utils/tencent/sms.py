
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from saas_29.settings import SMS_APPID, SMS_APPKEY, SMS_TEMPLATE
from django.http import HttpResponse, JsonResponse
import random, string
from django_redis import get_redis_connection

def send_sms_single(tpl, mobile_phone):
    """使用腾讯云发送短信
    tpl: 使用模板类型
    mobile_phone : 电话号
    """
    try:
        # 短信应用ｉｄ
        appid = SMS_APPID
        # 短信应用 SDK AppKey
        appkey = SMS_APPKEY
        # 需要发送短信的手机号码
        mobile_phone = mobile_phone
        # 签名
        sms_sign = "SaaSRenLei"
        # 验证码
        code = "".join(random.sample(string.digits, 4))
        # 模板参数
        if tpl == 'login':
            params = [code, 4]
        else:
            params = [code, 5]
        # 短信模板ID，需要在短信控制台中申请
        template_id = SMS_TEMPLATE[tpl]
    except KeyError:
        return {'errmsg':"请求方式有误--"}
    else:
        ssender = SmsSingleSender(appid, appkey)
        # res = ssender.send_with_param(
        #     86,
        #     mobile_phone,
        #     template_id,
        #     params,
        #     sign=sms_sign
        # )
        res = {'result': 0, 'errmsg': 'OK', 'ext': '', 'sid': '2106:208915069715888685778574505', 'fee': 1}
        print(res)
        if res['result'] == 0:
            conn = get_redis_connection('default')
            conn.set(mobile_phone, code, ex=60*5)
            return res

        return res


if __name__ == "__main__":
    send_sms_single('register',15561245051)
    # {'result': 0, 'errmsg': 'OK', 'ext': '', 'sid': '2106:208915069715888685778574505', 'fee': 1}
