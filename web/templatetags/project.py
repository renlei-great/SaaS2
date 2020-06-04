from django.template import Library
from django.urls import reverse

from web.models import ProjectUser, Project

register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    """用与创建通用前段模块"""
    user = request.tracer.user

    # 我创建的所有项目
    create_pros = Project.objects.filter(creator=user)
    # 我参与的所有项目
    user_pros = ProjectUser.objects.filter(user=user)

    return {"create_pros": create_pros, 'user_pros': user_pros}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    """完成被选中菜单的高亮"""
    li_list = [
        {'title': '概览', 'url': reverse('web:manage:dashboard', kwargs={'pro_id': request.tracer.project.id})},
        {'title': '问题', 'url': reverse('web:manage:issues', kwargs={'pro_id': request.tracer.project.id})},
        {'title': '统计', 'url': reverse('web:manage:statistics', kwargs={'pro_id': request.tracer.project.id})},
        {'title': '文件', 'url': reverse('web:manage:file', kwargs={'pro_id': request.tracer.project.id})},
        {'title': 'wiki', 'url': reverse('web:manage:wiki', kwargs={'pro_id': request.tracer.project.id})},
        {'title': '设置', 'url': reverse('web:manage:setting', kwargs={'pro_id': request.tracer.project.id})},
    ]

    for itme in li_list:
        if request.path_info.startswith(itme["url"]):
            itme['class'] = 'active'

    return {'li_list': li_list}