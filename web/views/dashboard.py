from django.shortcuts import render, redirect
from django.db.models import Count

from web.models import Issues, ProjectUser, Project


def dashboard(request, pro_id):
    """概览"""

    # 问题显示
    status_cho = Issues.status_choices
    status_dict = {}
    for key, text in status_cho:
        status_dict[key] = {'text': text, "count": 0}

    issues_data = Issues.objects.filter(project_id=pro_id).values('status')
    for item in issues_data:
        status_dict[item['status']]['count'] += 1

    # 项目参与者
    user_list = ProjectUser.objects.filter(project_id=pro_id).values('user__username')

    countext = {
        'status_dict': status_dict,  # 问题显示
        'user_list': user_list,  # 项目参与者
    }

    return render(request, 'dashboard.html', countext)