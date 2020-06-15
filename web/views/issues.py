import time

from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt

from web.forms.issues import IssuesForm, IssuesReplyForm
from web.models import Issues, Project, IssuesReply
from utils.web.pagination import Pagination


def issues(request, pro_id):
    """问题首页"""
    if request.method == 'GET':
        """显示"""
        form = IssuesForm(request)

        # 查询此项目下的所有问题
        issues_list = Issues.objects.filter(project_id=pro_id)

        # 分页
        page_object = Pagination(
            current_page=request.GET.get('page', 1),
            all_count=issues_list.count(),
            query_params=request.GET,
            pager_page_count=5,
            per_page=1,
            base_url=request.path_info
        )
        issues_object_list = issues_list[page_object.start:page_object.end]

        return render(request, 'issues.html', {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html()
        })

    """添加"""
    form = IssuesForm(request, data=request.POST)
    if not form.is_valid():
        return JsonResponse({'status': False, 'errors': form.errors})

    form.instance.project = request.tracer.project
    form.instance.creator = request.tracer.user
    form.save()

    return JsonResponse({'status': True})


# http://192.168.223.135:8000/web/manage/31/issues/4/detaile/
@csrf_exempt
def issues_detail(request, pro_id, iss_id):
    """问题详情页"""
    # 查询出此问题
    try:
        iss = Issues.objects.get(
            id=iss_id,
            project_id=request.tracer.project.id,
        )
    except Exception as e:
        return redirect(reverse('web:manage:issues'))

    if request.method == 'GET':
        """显示"""
        form = IssuesForm(request, instance=iss)

        return render(
            request,
            'issues_detail.html',
            {
                'form': form,
                'iss': iss,
            }
        )


@csrf_exempt
def init_issues_operate(request, pro_id, iss_id):
    """操作记录显示和添加"""
    # 查询此问题
    try:
        iss = Issues.objects.get(
            id=iss_id,
            project_id=request.tracer.project.id,
        )
    except Exception as e:
        return JsonResponse({'status': True, 'errors': '添加失败'})

    # 显示操作记录
    if request.method == 'GET':
        # 查询此问题下的所有记录
        iss_re_all = IssuesReply.objects.filter(issues=iss)
        items = []
        for iss_re in iss_re_all:
            items.append(
                {
                    'id': iss_re.id,
                    'reply_type': iss_re.get_reply_type_display(),
                    'creator': iss_re.creator.username,
                    'create_datetime': iss_re.create_datetime.strftime("%Y-%m-%d %H:%M"),
                    'content': iss_re.content,
                    'reply': iss_re.reply.id if iss_re.reply else False,
                }
            )

        return JsonResponse({'status': True, 'items': items})

    # －－－提交回复
    form = IssuesReplyForm(request.POST)
    reply = request.POST.get('reply')

    if not form.is_valid():
        return JsonResponse({'status': True, 'errors': form.errors})

    form.instance.issues = iss
    form.instance.creator = request.tracer.user
    if reply.isdecimal():
        form.instance.reply_id = int(reply)
    iss_re = form.save()

    # 组织返回前端的数据
    item = {
        'id': iss_re.id,
        'reply_type': iss_re.get_reply_type_display(),
        'creator': iss_re.creator.username,
        'create_datetime': iss_re.create_datetime.strftime("%Y-%m-%d %H:%M"),
        'content': iss_re.content,
        'reply': iss_re.reply.id if iss_re.reply else False,
    }

    return JsonResponse({'status': True, 'item': item})
