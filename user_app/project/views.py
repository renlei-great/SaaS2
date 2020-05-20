from django.shortcuts import render
from django import forms
from django.core.validators import RegexValidator
from django.http import JsonResponse

from user_app.project.models import Project


# Create your views here.


class CreateProjectForm(forms.Form):
    project_name = forms.CharField(max_length=20)
    color = forms.CharField(validators=[RegexValidator(r'^#.{6}', '颜色错误')])
    desc = forms.CharField(max_length=300)


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



