from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from web.models import Issues, ProjectUser, Project


def statistics(request, pro_id):
    """统计"""
    return render(request, 'statistics.html')


def statistics_priority(request, pro_id):
    """按照优先级生成饼图"""
    # 获取数据
    start = request.GET.get('start')
    end = request.GET.get('end')

    # 组织字段
    data_dict = {}
    for key, text in Issues.priority_choices:
        data_dict[key] = {'name': text, 'y': 0}

    # 查询出所有范围内的问题
    qury_issues = Issues.objects.filter(
        project_id=pro_id,
        create_datetime__gte=start,
        create_datetime__lt=end).values('priority').annotate(ct=Count('id'))

    # 组织返回数据
    for qury in qury_issues:
        data_dict[qury['priority']]['y'] = qury['ct']

    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request, pro_id):
    """生成人员工作进度"""
    # 获取数据
    start = request.GET.get('start')
    end = request.GET.get('end')

    # 组织返回的字典
    '''[{
        name: '新建',
        data: [5, 3, 4]
    }, {
        name: '处理中',
        data: [2, 2, 3]
    }, {
        name: '啊啊',
        data: [3, 4, 4]
    }]'''
    series = []
    for key, text in Issues.status_choices:
        series.append({'name': text, 'data': []})

    # 返回的categories
    categories = []

    # 查询出此项目下的所有人员
    users = []
    users.append(request.tracer.project.creator)
    user_pro = ProjectUser.objects.filter(project_id=pro_id)
    for user in user_pro:
        users.append(user.user)

    # 查询出所有有指派的问题
    issuess = Issues.objects.filter(project_id=pro_id,)

    # 遍历每一个用户，找出指派给此用户的所有问题
    for user in users:
        judge = []
        # 找到问题并进行分组，找出每一个问题的状态有多少个
        user_issues_status = issuess.filter(
            assign=user,
            create_datetime__gte=start,
            create_datetime__lt=end,
        ).values('status').annotate(ct=Count('id'))

        if user_issues_status:
            # 是有东西
            # 组织前期数据
            user_issues_status = list(user_issues_status)
            for status in user_issues_status:
                judge.append(status['status'])
            for i in range(1, len(Issues.status_choices) + 1):
                if i in judge:
                    continue
                user_issues_status.append({'status': i, 'ct': 0})
                # 如果上面报错，那么九江ｕｓｅｒ_issues_status 转化为列表

            # for i in range(len(Issues.status_choices)):
                # a = len(user_issues)
                # if i < len(user_issues):
                #     break
                # issues = user_issues_status[i]
                # series[issues['status']-1]['data'].append(issues['ct'])
                # ape = issues['ct'] if issues['status']-1] == i else 0
                # series[i]['data'].append(
                #     issues['ct'] if issues['status'] - 1 == i else 0
                # )

            #　遍历每一个用户所有的状态进行添加
            # i = 0
            for issues in user_issues_status:
                series[issues['status']-1]['data'].append(issues['ct'])
                # series[issues['status']-1]['data'].append(issues['ct'])
            categories.append(user.username)

    # 找出此项目下的所有未指派的问题
    user_issues = issuess.filter(
        assign=None,
        create_datetime__gte=start,
        create_datetime__lt=end,
    ).values('status').annotate(ct=Count('id'))
    # 　遍历未指派的问题所有的状态进行添加
    for issues in user_issues:
        # series[-1]['data'].append(issues['ct'])
        series[issues['status'] - 1]['data'].append(issues['ct'])
    categories.append('未指派')

    data = {
        'series': series,
        'categories': categories,
    }

    return JsonResponse({'status': True, 'data': data})
