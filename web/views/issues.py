import time, json

from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

from web.forms.issues import IssuesForm, IssuesReplyForm
from web.models import Issues, Project, IssuesReply, ProjectUser
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
    """问题详情编辑页"""

    def org_pro_user():
        """功能:
            组织本项目下的所有用户
            """
        # 组织此项目下的所有用户
        pro_users = ProjectUser.objects.filter(project_id=pro_id)
        pro_user_list = [request.tracer.project.creator, ]
        for pro_user in pro_users:
            pro_user_list.append(pro_user.user)

        return pro_user_list

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

    # 变更问题　－－　修改
    # 接收数据
    date_dict = json.loads(request.body.decode())  # 前段传来的数据
    name = date_dict.get('name')
    value = date_dict.get('value', None)
    value = value if value else None

    obj_filed = Issues._meta.get_field(name)  # 取出字段对象

    # 保存数据库中并在操作记录中显示的模板
    template_text = mark_safe('<span style="font-size: 20px"><b>{name}</b></span> 更改为: <b>{value}</b>')

    # 判断是否是无改变数据
    if str(getattr(iss, name)) == value:
        return JsonResponse({'status': False, 'error': '无改变'})

    # 进行校验数据的合法性
    '''
    文本 : subject - desc - start_date - end_date
    FK : issues_type- parent - module - assign
        1.判断是否越界
        2.判断是否为空，如果为空，字段是否容许为空
        3. 特殊字段assign-需要到ProjectUser表中去进行判断
            需要判断当前创建者是不是，还有和当前项目有关系的用户是不是
    choices : status - priority - mode
    M2M : attention
    '''
    # 情况１　－－　文本
    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value and name in ['subject', 'desc']:
            return JsonResponse({'status': False, 'error': '该字段不可为空'})
        content = template_text.format(name=obj_filed.verbose_name, value=value if value else '空')
    # 情况２　－　ＦＫ
    elif name in ['issues_type', 'parent', 'module', 'assign']:
        # 如果值为空
        if not value:
            # 此字段不容许为空
            if not obj_filed.null:
                return JsonResponse({'status': False, 'error': '该字段不可为空'})
            content = template_text.format(name=obj_filed.verbose_name, value=value if value else '空')
        else:  # 值不为空
            # 修改的是指派给谁
            if name == 'assign':
                pro_user_list = org_pro_user()
                jubge = True
                for user in pro_user_list:
                    if str(user.id) == value:
                        jubge = False
                        content = template_text.format(name=obj_filed.verbose_name, value=user.username)
                        break
                if jubge:
                    return JsonResponse({'status': False, 'error': '滚犊子'})
            # 进行判断此值是不是在范围中
            else:
                rel_objs = obj_filed.rel.model.objects.filter(project_id=pro_id)
                jubge = True
                for obj in rel_objs:
                    if str(obj.id) == value:
                        jubge = False
                        content = template_text.format(name=obj_filed.verbose_name, value=obj.subject if name == 'parent' else obj.title)
                        break
                if jubge:
                    return JsonResponse({'status': False, 'error': '滚犊子'})

    # 情况3 - choices
    elif name in ['status', 'priority', 'mode']:
        # 值为空
        if not value:
            # 字段不容许为空
            if not obj_filed.null:
                return JsonResponse({'status': False, 'error': '该字段不可为空'})
            else:
                content = template_text.format(name=obj_filed.verbose_name, value='空')
        else:
            # 值不为空
            jubge = True
            for index, text in obj_filed.choices:
                # 遍历choices中的每一个元素
                if value == str(index):
                    jubge = False
                    content = template_text.format(name=obj_filed.verbose_name,value=text)
                    break
            if jubge:
                return JsonResponse({'status': False, 'error': '滚犊子'})

    # 情况4 - M2M
    elif name == 'attention':
        # 值为空
        if not value:
            value = []
            content = template_text.format(name=obj_filed.verbose_name, value='空')
        else:
            # 值不为空
            pro_user_list = org_pro_user()
            for user in pro_user_list:
                if str(user.id) in value:
                    pass







    # 验证通过-修改数据库数据
    try:
        setattr(iss, name, value)
    except ValueError as e:
        # 第二方案
        try:
            setattr(iss, name + '_id', value)
        except ValueError as e:
            print(f'保存报错{e}')
            return JsonResponse({'status': False, 'error': '更改出错'})

    iss.save()

    iss_re = IssuesReply.objects.create(
        reply_type=1,
        issues=iss,
        content=content,
        creator=request.tracer.user,
    )

    item = {
        'id': iss_re.id,
        'reply_type': iss_re.get_reply_type_display(),
        'creator': iss_re.creator.username,
        'create_datetime': iss_re.create_datetime.strftime("%Y-%m-%d %H:%M"),
        'content': iss_re.content,
        'reply': iss_re.reply.id if iss_re.reply else False,
    }

    return JsonResponse({'status': True, 'item': item})


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

    # －－－提交回复－－添加
    form = IssuesReplyForm(request.POST)
    reply = request.POST.get('reply')

    if not form.is_valid():
        return JsonResponse({'status': True, 'errors': form.errors})

    form.instance.issues = iss
    form.instance.creator = request.tracer.user
    if reply:
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
