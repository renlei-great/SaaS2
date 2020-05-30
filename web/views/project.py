from django.http import JsonResponse
from django.shortcuts import render, redirect

from web.models import Project, ProjectUser
from web.forms.project import ProjectForm


def project(request):
    """项目"""
    user = request.tracer.user
    if request.method == 'GET':
        """显示项目首页"""
        pro_form = ProjectForm(request)
        # 查询此用户创建的所有项目
        pro_list = Project.objects.filter(creator=user)
        # 查询此用户参与的所有项目
        pro_user_list = ProjectUser.objects.filter(user=user)

        # 查询创建项目的星标项目
        pro_stars = pro_list.filter(is_star=True)
        # 查寻参与项目的星标项目
        pro_user_stars = pro_user_list.filter(is_star=True)
        # 合并星标项目
        pro_stars = list(pro_stars)  # .extend(list(pro_user_stars))

        for star in pro_stars:
            star.cls = 'my'  # 动态添加属性,表示是什么类型的星标

        for star in pro_user_stars:
            star.cls = 'join'
            pro_stars.append(star.project)

        countxt = {'pro_list': pro_list,
                   'pro_user_list': pro_user_list,
                   'pro_stars': pro_stars,
                   'pro_form': pro_form,
                   }

        return render(request, 'project_list.html', countxt)

    if request.method == 'POST':
        """创建一个项目"""
        user = request.tracer.user
        pro_form = ProjectForm(request, request.POST)
        if not pro_form.is_valid():
            return JsonResponse({'stutic': False, 'error': pro_form.errors})

        pro_form.instance.creator = user
        pro_form.save()



        return JsonResponse({'stutic': True})


def asterisk(request, pro_type):
    """添加或取消星标"""
    user = request.tracer.user
    # 获取数据
    pro_id = request.GET.get('pro_id')
    # pro_type = request.GET.get('pro_type')
    print(pro_type)

    # 去数据库中查询此项目是否星标
    try:
        pro_id = int(pro_id)
        if pro_type == 'my':
            pro = Project.objects.get(pk=pro_id, creator=user)
        elif pro_type == 'join':
            pro = ProjectUser.objects.get(project=pro_id, user=user)
    except Exception as e:
        # 无此项目
        # return JsonResponse({'status': False, 'error': '无此项目'})
        return redirect('web:project')

    if pro.is_star:
        # 取消星标
        pro.is_star = False
    else:
        # 添加星标
        pro.is_star = True

    pro.save()
    # return JsonResponse({'status': True})
    return redirect('web:project')