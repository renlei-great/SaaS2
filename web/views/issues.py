from django.http import JsonResponse
from django.shortcuts import render, redirect

from web.forms.issues import IssuesForm
from web.models import Issues, Project


def issues(request, pro_id):
    """问题首页"""
    if request.method == 'GET':
        """显示"""
        form = IssuesForm(request)

        # 查询此项目下的所有问题
        issues_object_list = Issues.objects.filter(project_id=pro_id)

        return render(request, 'issues.html', {
            'form': form,
            'issues_object_list': issues_object_list
        })

    """添加"""
    form = IssuesForm(request, data=request.POST)
    if not form.is_valid():
        return JsonResponse({'status': False, 'errors': form.errors})

    form.instance.project = request.tracer.project
    form.instance.creator = request.tracer.user
    form.save()

    return JsonResponse({'status': True})