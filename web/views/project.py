from django.http import JsonResponse
from django.shortcuts import render

from web.models import Project
from web.forms.project import ProjectForm


def project(request):
    """项目"""
    user = request.tracer
    if request.method == 'GET':
        """显示项目首页"""
        pro_form = ProjectForm(request)
        # 查询此用户创建的所有项目
        # pro_list = Project.objects.filter(creator=user.pk)
        #
        # # 查询星标项目
        # asterisks = pro_list.filter(asterisk=True)
        #
        # countxt = {'pro_list': pro_list, 'asterisks': asterisks}

        return render(request, 'project_list.html', {'pro_form': pro_form})

    if request.method == 'POST':
        """创建一个项目"""
        user = request.tracer.user
        pro_form = ProjectForm(request, request.POST)
        if not pro_form.is_valid():
            return JsonResponse({'stutic': False, 'error': pro_form.errors})

        pro_form.instance.creator = user
        pro_form.save()

        return JsonResponse({'stutic': True})