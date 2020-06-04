from django.shortcuts import render
from django import forms
from django.core.validators import RegexValidator
from django.http import JsonResponse
import json
import os
from sts.sts import Sts

from user_app.project.models import Project
from saas_29.settings import SecretId, SecretKey


# Create your views here.


class CreateProjectForm(forms.Form):
    project_name = forms.CharField(max_length=20)
    color = forms.CharField(validators=[RegexValidator(r'^#.{6}', '颜色错误')])
    desc = forms.CharField(max_length=300)


class WikiFileForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea())


def wiki_st(request):
    """前端获取临时秘钥"""
    # print('进来了')
    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': SecretId,
        # 固定密钥
        'secret_key': SecretKey,
        # 换成你的 bucket
        'bucket': 'user-id-8-user-mobile-15561245051-1dba-1302000219',
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
    # print(res)
    return JsonResponse(res)


def wiki(request):
    """显示提交页面"""
    wiki_form = WikiFileForm()
    return render(request, 'file/wiki.html', {'wiki_form': wiki_form})


def project(request):
    """项目"""
    user = request.tracer
    if request.method == 'GET':
        """新建项目首页"""
        # 查询此用户创建的所有项目
        pro_list = Project.objects.filter(creator=user.pk)

        # 查询星标项目
        asterisks = pro_list.filter(asterisk=True)

        countxt = {'pro_list': pro_list, 'asterisks': asterisks}

        return render(request, 'project/project.html', countxt)

    if request.method == 'POST':
        """创建一个项目"""
        user = request.tracer
        cp_get = CreateProjectForm(request.POST)
        if not cp_get.is_valid():
            return JsonResponse({'stutic': False})
        project_name = cp_get.cleaned_data['project_name']
        desc = cp_get.cleaned_data['desc']
        color = cp_get.cleaned_data['color']
        creator = user.id
        Project.objects.create(project_name=project_name,
                               desc=desc,
                               color=color,
                               creator_id=creator,
                               )

        return JsonResponse({'stutic': True})


def asterisk(request):
    """添加或取消星标"""
    # 获取数据
    pro_id = request.GET.get('pro_id')

    # 去数据库中查询此项目是否星标
    try:
        pro_id = int(pro_id)
        pro = Project.objects.get(pk=pro_id)
    except Exception as e:
        # 无此项目
        return JsonResponse({'status': False, 'error': '无此项目'})

    if pro.asterisk:
        # 取消星标
        pro.asterisk = False
    else:
        # 添加星标
        pro.asterisk = True

    pro.save()
    return JsonResponse({'status': True})



