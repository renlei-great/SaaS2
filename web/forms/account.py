
from django import forms
from django.http import HttpResponse

from web.models import UserInfo
# 自定义表单的正则匹配
from django.core.validators import RegexValidator


class RegisterForm(forms.ModelForm):
    # 自定义表单的正则匹配
    mobile_phpne = forms.CharField(label="手机", validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d[9]', '手机格式错误'),])
    # 自定义输入框的格式
    password = forms.CharField(label="密码", widget=forms.PasswordInput())

    password1 = forms.CharField(label="再次输入密码", widget=forms.PasswordInput())
    code = forms.CharField(label="验证码")

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 'password1','mobile_phpne',  'code']

    def clean(self):
        password = self.data.get['password', 1]
        password1 = self.data.get['password1', 2]
        if password != password1:
            return HttpResponse('两次密码不一致')
        return password

    def clean_mobile_phpne(self):
        mobile_phpne = self.data.get['mobile_phpne']
        user = UserInfo()
        qy = user.objects.filter(mobile_phpne=mobile_phpne)
        if qy:
            raise forms.ValidationError('该手机号已注册')
        return mobile_phpne

    def __init__(self, *args, **kwargs):
        """重写给每个字段动态添加属性"""
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)