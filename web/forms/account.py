
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse

from utils.tencent.sms import send_sms_single
from web.models import UserInfo
# 自定义表单的正则匹配
from django.core.validators import RegexValidator
from saas_29.settings import SMS_TEMPLATE


class RegisterForm(forms.ModelForm):
    # 自定义表单的正则匹配
    mobile_phpne = forms.CharField(label="手机",min_length=11, max_length=11, required=True, validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d[9]', '手机格式错误'),])
    # 自定义输入框的格式
    password = forms.CharField(label="密码", required=True, widget=forms.PasswordInput())

    password1 = forms.CharField(label="再次输入密码", required=True, widget=forms.PasswordInput())
    code = forms.CharField(label="验证码", required=True,)

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 'password1','mobile_phpne',  'code']

    def clean(self):
        password = self.changed_data.get['password', 1]
        password1 = self.changed_data.get['password1', 2]
        if password != password1:
            raise ValidationError('两次密码不一致')
        return self.changed_data

    def clean_mobile_phpne(self):
        mobile_phpne = self.changed_data.get['mobile_phpne']

        # 查看手机号是否被注册
        qy = UserInfo.objects.filter(mobile_phpne=mobile_phpne)
        if qy:
            raise ValidationError('该手机号已注册')

        # 查看短信模板是否正确
        tpl = self.request.POST.get('tpl')
        if not SMS_TEMPLATE.get(tpl):
            raise ValidationError('请求格式错误')

        return mobile_phpne

    def __init__(self, *args, **kwargs):
        """重写给每个字段动态添加属性"""
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)


class SendSmSFoem(forms.Form):
    """发送短信表单"""
    mobile_phpne = forms.CharField(label="手机",min_length=11, max_length=11, required=True, validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d[9]', '手机格式错误'),])

    def clean_mobile_phpne(self):
        mobile_phpne = self.changed_data['mobile_phpne']

        # 查看手机号是否被注册
        qy = UserInfo.objects.filter(mobile_phpne=mobile_phpne)
        if qy:
            raise ValidationError('该手机号已注册')

        # 查看短信模板是否正确
        tpl = self.request.GET.get('tpl')
        if not SMS_TEMPLATE.get(tpl):
            raise ValidationError('请求格式错误')

        # 发送短信验证码
        res = send_sms_single(tpl, mobile_phpne)
        if res['result'] != 0:
            raise ValidationError('短信发送失败：{}'.format(res['errmsg']))

        return mobile_phpne

    def __init__(self,request,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

