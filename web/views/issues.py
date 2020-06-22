import time, json
import uuid
import bcrypt

from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django_redis import get_redis_connection

from web.forms.issues import IssuesForm, IssuesReplyForm, IssuesProjectInvite
from web.models import Issues, Project, IssuesReply, ProjectUser, Transaction
from utils.web.pagination import Pagination


def org_pro_user(request):
    """功能:
        组织本项目下的所有用户
        """
    # 组织此项目下的所有用户
    pro_users = ProjectUser.objects.filter(project_id=request.tracer.project.id)
    pro_user_list = [request.tracer.project.creator, ]
    for pro_user in pro_users:
        pro_user_list.append(pro_user.user)

    return pro_user_list

class SreachIssuesIter:
    """动态生成model中的字段choices中的选项变成前段的复选框"""
    def __init__(self, name, request):
        self.name = name
        self.request = request

    def __iter__(self):
        # 使用yield直接写一个迭代器
        # 获取字段对象
        filed = Issues._meta.get_field(self.name)

        # 获取字段对象的choices
        if filed.rel:
            filed_choices_list = []
            filed_fk_dict = filed.rel.model.objects.filter(project=self.request.tracer.project).values('id', 'title')
            for dic in filed_fk_dict:
                filed_choices_list.append((dic['id'], dic['title']))
        else:
            filed_choices_list = filed.choices


        # '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
        tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck}/><label>{text}</label></a>'

        # 获取URL中的信息
        url_info = self.request.path_info
        url_dict = self.request.GET.copy()
        url_dict._mutabla = True  # 设置此值，url_dict才能被修改

        for index, value in filed_choices_list:
            '''
            设置URL的整体思想就是：
                先将URL中是此name的所有的参数都取出来，使用getlist获取到一个列表
                如果此刻循环的这个index和这个getlist
            '''
            # 获取URL参数列表
            get_list = self.request.GET.getlist(self.name)

            # 判断当前的id是否被选择
            if str(index) in get_list:
                # 被选择
                ck = 'checked'
                get_list.remove(str(index))
            else:
                # 没有选择进行添加
                ck = ""
                get_list.append(str(index))

            # 组织URL
            url_dict.setlist(self.name, get_list)
            if 'page' in url_dict:
                url_dict.pop('page')

            # 将字段变为URL get请求参数
            param_url = url_dict.urlencode()

            if param_url:
                url = f'{url_info}?{param_url}'
            else:
                url = url_info

            yield mark_safe(tpl.format(url=url, ck=ck, text=value))


class SreachAssignIter:
    """动态生成model中的字段指派中的选项变成前段的复选框"""
    def __init__(self, name, request):
        self.name = name
        self.request = request

    def __iter__(self):
        # 使用yield直接写一个迭代器
        # 获取字段对象
        filed = Issues._meta.get_field(self.name)

        # 获取字段对象,组织数据
        filed_choices_list = []
        pro_user_list = org_pro_user(self.request)
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")

        # 遍历每一个对象，得到一个[(1,'name'),(2, 'name),(3, 'name')]
        for user in pro_user_list:
            filed_choices_list.append((user.id, user.username))

        tpl = "<option value='{url}' {ck} >{text}</option>"

        # 获取URL中的信息
        url_info = self.request.path_info
        url_dict = self.request.GET.copy()
        url_dict._mutabla = True  # 设置此值，url_dict才能被修改

        for index, value in filed_choices_list:
            '''
            设置URL的整体思想就是：
                先将URL中是此name的所有的参数都取出来，使用getlist获取到一个列表
                如果此刻循环的这个index和这个getlist
            '''
            # 获取URL参数列表
            get_list = self.request.GET.getlist(self.name)

            # 判断当前的id是否被选择
            if str(index) in get_list:
                # 被选择
                ck = 'selected'
                get_list.remove(str(index))
            else:
                # 没有选择进行添加
                ck = ""
                get_list.append(str(index))

            # 组织URL
            url_dict.setlist(self.name, get_list)
            if 'page' in url_dict:
                url_dict.pop('page')

            # 将字段变为URL get请求参数
            param_url = url_dict.urlencode()

            if param_url:
                url = f'{url_info}?{param_url}'
            else:
                url = url_info

            yield mark_safe(tpl.format(url=url, ck=ck, text=value))
        yield mark_safe("</select>")


def issues(request, pro_id):
    """问题首页"""
    if request.method == 'GET':
        """显示"""
        form = IssuesForm(request)
        # 做问题筛选，进行拼接
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        get_filter = {}
        for name in allow_filter_name:
            value = request.GET.getlist(name)
            if not value:
                continue
            if name == 'issues_type':
                get_filter[f'{name}_id__in'] = value
            else:
                get_filter[f'{name}__in'] = value

        # 查询此项目下的所有问题
        issues_list = Issues.objects.filter(project_id=pro_id).filter(**get_filter)

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

        # 获取状态的筛选迭代器
        filter_list = []
        for title_name in ['issues_type', 'status', 'priority', 'assign', 'attention']:
            title = Issues._meta.get_field(title_name).verbose_name
            if title_name in ['assign', 'attention']:
                # 获取的是select框
                filter = SreachAssignIter(name=title_name, request=request)
            else:
                # 获取的是多选框
                filter = SreachIssuesIter(name=title_name, request=request)
            filter_list.append({'title': title, 'filter': filter})

        # 邀请成员表单
        invite_form = IssuesProjectInvite(request)

        return render(request, 'issues.html', {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': filter_list,
            'invite_form': invite_form
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
                pro_user_list = org_pro_user(request)
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
            pro_user_list = org_pro_user(request)
            user_dict = {}
            for user in pro_user_list:
                # 添加所有的用到变成一个字段 格式 ID : name
                user_dict[str(user.id)] = user.username

            # 遍历前端传来的每一个id进行判断是否超出范围
            usernames = ''
            for id in value:
                if id in user_dict:
                    # 在范围内
                    usernames += user_dict[id] + ', '
                else:
                    return JsonResponse({'status': False, 'error': '数据出错，请重新执行操作'})
            content = template_text.format(name=obj_filed.verbose_name, value=usernames)

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


def invite_code(request, pro_id):
    """生成邀请码"""
    invite_form = IssuesProjectInvite(request, data=request.POST)

    if not invite_form.is_valid():
        return JsonResponse({'status': False, 'error': invite_form.errors})

    # 校验用户
    if request.tracer.project.creator.id != request.tracer.user.id:
        invite_form.add_error('count', '权限错误')
        return JsonResponse({'status': False, 'error': invite_form.errors})

    # 获取数据
    period = invite_form.cleaned_data['period']
    count = invite_form.cleaned_data['count']

    # 组织返回的邀请码url地址
    try:
        period = int(period) * 60
        # period = 3
    except Exception:
        invite_form.add_error('period', '输入有误')
        return JsonResponse({'status': False, 'error': invite_form.errors})

    # 生成加密邀请码
    str_redis = str(uuid.uuid4())[0:5].encode()
    code = bcrypt.hashpw(str_redis, bcrypt.gensalt()).decode()
    # 组织URL
    # http://192.168.223.135:8000/web/manage/31/issues
    # request.scheme 获取请求协议
    # request.get_host 获取请求主机名
    # path 携带的参数
    path = reverse('web:manage:add_user_pro', kwargs={'pro_id': pro_id})
    ret_url = f'{request.scheme}://{request.get_host()}{path}?code={code}'

    # 向redis添加数据
    con = get_redis_connection()
    con.hmset(f'pro_{pro_id}', {
        'pro_id': pro_id,
        'count': count,
        'use_count': 0,
        'code': str_redis,
    })

    con.expire(f'pro_{pro_id}', period)

    return JsonResponse({'status': True, 'url': ret_url})


def add_user_pro(request, pro_id):
    """为项目添加成员"""
    # 获取redis中的code
    code = request.GET.get('code', '')
    if not code:
        return render(request, 'invite_join.html', {'status': False, 'error': '链接无效'})

    # 链接redis
    con = get_redis_connection()
    # 组织redis数据库中的键
    key = f'pro_{pro_id}'
    is_judbge = con.hexists(key, 'code')

    # 查询redis中存放的code，验证邀请链接是否有效
    if is_judbge:
        redis_code = con.hmget(key, 'code')
    else:
        return render(request, 'invite_join.html', {'status': False, 'error': '链接已超时或不存在'})
    if not bcrypt.checkpw(redis_code[0], code.encode()):
        return render(request, 'invite_join.html', {'status': False, 'error': '链接无效'})

    # 该用户是否已经加入此项目
    pro = Project.objects.filter(creator=request.tracer.user, id=pro_id).exists()
    pro_user = ProjectUser.objects.filter(project_id=pro_id, user=request.tracer.user).exists()
    if pro or pro_user:
        return render(request, 'invite_join.html', {'status': False, 'error': '您已经在此项目当中'})

    # 该链接邀请人数是否达到最大人数
    count = int(con.hmget(key, 'count')[0].decode())
    use_count = int(con.hmget(key, 'use_count')[0].decode())
    if use_count +1 > count:
        return render(request, 'invite_join.html', {'status': False, 'error': '此链接已达到邀请人数限制'})

    project = Project.objects.get(id=int(pro_id))

    # 查看此套餐的最大人数限制是否足够
    # 获取用户的权限
    obj_trans = Transaction.objects.filter(user=project.creator, status=2).order_by('-id').first()
    if project.join_count + 1 > int(obj_trans.price_policy.pro_member):
        return JsonResponse({'status': False, 'error': '此项目已达到邀请人数限制，请升级套餐'})

    # 验证通过，执行相应的增加
    # use_count += 1
    # con.hmset(key, {'use_count': use_count})
    con.hincrby(key, 'use_count', amount=1)
    join_count = project.join_count
    project.join_count += 1
    project.save()

    # 向数据库添加项目
    ProjectUser(
        project_id=pro_id,
        user=request.tracer.user,
    ).save()
    return render(request, 'invite_join.html', {'status': True, 'pro_id': pro_id})

