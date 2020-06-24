import datetime, time

from django.shortcuts import render, redirect
from django.db.models import Count
from django.http import HttpResponse, JsonResponse

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

    # 动态
    top_ten_object = Issues.objects.filter(project_id=pro_id).order_by('-create_datetime')[0:5]

    countext = {
        'status_dict': status_dict,  # 问题显示
        'user_list': user_list,  # 项目参与者
        'top_ten_object': top_ten_object  # 动态
    }

    return render(request, 'dashboard.html', countext)


def issues_chart(request, pro_id):
    """在概览页面生成highcharts所需的数据"""

    # 组织一个字典里边放30天的数据
    # 当天时间
    today = datetime.datetime.now().date()
    date_dict = {}
    for i in range(30):
        date = today - datetime.timedelta(days=i)
        a = time.mktime(date.timetuple())
        date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    # 查询出前30天时间的数据
    res = Issues.objects.filter(
        project_id=pro_id,
        create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={'ctime': "DATE_FORMAT(web_issues.create_datetime,'%%Y-%%m-%%d')"}
    ).values('ctime').annotate(ct=Count('id'))
    print(res.query)
    for item in res:
        date_dict[item['ctime']][1] = item['ct']

    return JsonResponse({'status': True, 'data': list(date_dict.values())})