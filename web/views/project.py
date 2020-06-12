import uuid, re

from django.http import JsonResponse
from django.shortcuts import render, redirect
from pypinyin import pinyin, lazy_pinyin, Style
from qcloud_cos import CosClientError

from web.models import Project, ProjectUser
from web.forms.project import ProjectForm
from utils.tencent.cos import create_cos


def project(request):
    """项目"""
    user = request.tracer.user
    if request.method == 'GET':
        """显示项目首页"""
        pro_form = ProjectForm(request)
        # 查询此用户创建的所有项目
        pro_list = Project.objects.filter(creator=user)
        # 查询此用户参与的所有项目
        pro_user_list = ProjectUser.objects.filter(user=user)

        # 查询创建项目的星标项目
        pro_stars = pro_list.filter(is_star=True)
        # 查寻参与项目的星标项目
        pro_user_stars = pro_user_list.filter(is_star=True)
        # 合并星标项目
        pro_stars = list(pro_stars)  # .extend(list(pro_user_stars))

        for star in pro_stars:
            star.cls = 'my'  # 动态添加属性,表示是什么类型的星标

        for star in pro_user_stars:
            star.cls = 'join'
            pro_stars.append(star.project)

        countxt = {'pro_list': pro_list,
                   'pro_user_list': pro_user_list,
                   'pro_stars': pro_stars,
                   'pro_form': pro_form,
                   }

        return render(request, 'project_list.html', countxt)

    if request.method == 'POST':
        """创建一个项目"""
        user = request.tracer.user
        pro_form = ProjectForm(request, request.POST)
        if not pro_form.is_valid():
            return JsonResponse({'stutic': False, 'error': pro_form.errors})

        # 组织桶名
        pro_name_str = pro_form.cleaned_data['project_name']
        pro_name_list = pinyin(pro_name_str, style=Style.FIRST_LETTER)
        pro_name = ",".join(re.findall('\w+', str(pro_name_list))).replace(',', '')
        bucket = f'user-id-{user.id}-pro-name-{pro_name}-{str(uuid.uuid4())[1:5]}-1302000219'

        # 链接cos
        client = create_cos()
        try:
            # 创建桶
            response = client.create_bucket(
                Bucket=bucket,
                ACL='public-read'
            )
        except CosClientError as e:
            pro_form.add_error('project_name', '项目名格式是非法的，只允许数字、字母和- !')
            return JsonResponse({'stutic': False, 'error': pro_form.errors})

        # 数据库中创建项目
        pro_form.instance.creator = user
        pro_form.instance.bucket = bucket
        pro_form.save()

        cors_config = {
            'CORSRule': [
                {
                    'AllowedOrigin': '*',
                    'AllowedMethod': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
                    'AllowedHeader': '*',
                    'ExposeHeader': '*',
                    'MaxAgeSeconds': 500,
                }
            ]
        }

        client.put_bucket_cors(
            Bucket=pro_form.instance.bucket,
            CORSConfiguration=cors_config,
        )

        return JsonResponse({'stutic': True})


def asterisk(request, pro_type):
    """添加或取消星标"""
    user = request.tracer.user
    # 获取数据
    pro_id = request.GET.get('pro_id')
    # pro_type = request.GET.get('pro_type')
    # print(pro_type)

    # 去数据库中查询此项目是否星标
    try:
        pro_id = int(pro_id)
        if pro_type == 'my':
            pro = Project.objects.get(pk=pro_id, creator=user)
        elif pro_type == 'join':
            pro = ProjectUser.objects.get(project=pro_id, user=user)
    except Exception as e:
        # 无此项目
        # return JsonResponse({'status': False, 'error': '无此项目'})
        return redirect('web:project')

    if pro.is_star:
        # 取消星标
        pro.is_star = False
    else:
        # 添加星标
        pro.is_star = True

    pro.save()
    # return JsonResponse({'status': True})
    return redirect('web:project')