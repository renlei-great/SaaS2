import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from sts.sts import Sts
from django.views.decorators.csrf import csrf_exempt

from web.models import FileManage
from web.forms.file import FileForm
from utils.tencent.cos import create_cos, cos_acquire_sts


def file(request, pro_id):
    if request.method == 'GET':
        """显示文件管理首页"""
        file_id = request.GET.get('file_id', "")
        files_list = []

        # 判断是否进入文件夹
        if file_id.isdecimal():
            # 进入了某一个文件夹
            files = FileManage.objects.filter(
                project_id=pro_id,
                update_user=request.tracer.user,
                parent=file_id)

            file = FileManage.objects.get(id=file_id)

            while file:
                files_list.append({'name': file.file_name, 'id': file.id})
                file = file.parent

        else:
            # 查询根文件和文件夹
            files = FileManage.objects.filter(project_id=pro_id, parent=None)

        file_form = FileForm(request)

        return render(request, 'file.html', {'files': files, 'file_form': file_form, 'files_list': files_list[::-1]})

    if request.method == 'POST':
        """添加文件夹"""
        fid = request.POST.get('fid', "")
        file_id = request.GET.get('file_id', "")
        if fid.isdecimal():
            # 修改文件夹
            try:
                # 获取文件夹对象
                file_obj = FileManage.objects.get(id=fid, project=request.tracer.project, update_user=request.tracer.user)
            except Exception as e:
                print(f'file.py 报错：{e}')
                return JsonResponse({'status': False, 'error': {'未知': '没有此文件'}})
            # 交给表单处理
            file_form = FileForm(request, request.POST, instance=file_obj)
        else:
            # 新建文件夹
            file_form = FileForm(request, request.POST)

        if not file_form.is_valid():
            return JsonResponse({'status': False, 'error': file_form.errors})

        file_form.instance.project_id = pro_id
        file_form.instance.file_cla = 2
        file_form.instance.update_user = request.tracer.user
        if file_id.isdecimal():
            file_form.instance.parent_id = file_id

        file_form.save()

        return JsonResponse({'status': True})


def add_file(request, pro_id):
    """创建文件"""
    # 获取数据
    project = request.tracer.project
    user = request.tracer.user
    file_id = request.GET.get('file_id', "")


    return HttpResponse('ok')


# http://192.168.223.134:8000/web/manage/6/file_del?file_id=1
def file_del(request, pro_id):
    """删除文件"""
    # 获取文件或文件夹的id
    pid = request.GET.get('fid', "")
    user = request.tracer.user
    project = request.tracer.project

    if pid.isdecimal():
        # 获取此文件或文件夹对象
        try:
            file = FileManage.objects.get(id=pid, update_user=user, project=project)
        except Exception as e:
            print(f'删除文件时报错 line 81: {e}')
            return JsonResponse({'status': False, 'error': {'类型': '没有此文件'}})

    file_size = 0
    file_list = [file,]
    key_list = []

    # 判断是删除文件还是文件夹
    for file in file_list:
        files = FileManage.objects.filter(parent=file)
        if not files:
            continue
        for f in files:
            if f.file_cla == 2:
                # 文件夹
                file_list.append(f)
            else:
                # 文件
                file_size += f.file_size
                key_list.append({'Key': f.key})

    # 创建cos对象并进行删除
    client = create_cos()
    client.delete_objects(
        Bucket=project.bucket,
        Delete={
            "Quiet": "true",
            "Object": key_list
        }
    )

    # 归还空间
    project.used_space = project.used_space - file_size

    # 删除文件或文件夹:删除时不能复制？
    FileManage.objects.get(id=pid, project=project, update_user=user).delete()

    # 成功返回
    return JsonResponse({'status': True})


# http://192.168.223.134:8000/web/manage/23/acquire/sts/
@csrf_exempt
def acquire_sts(request, pro_id):
    """前端获取临时凭证"""
    # 获取文件参数
    file_name = request.POST.get('file_name')
    file_size = request.POST.get('file_size')
    per_file_size = int(request.tracer.price_policy.per_file_size) * 1024 * 1024
    print(per_file_size, type(per_file_size))
    # 查询用户的套餐
    if int(file_size) > per_file_size:
        return JsonResponse({'status': False, 'error': '单文件超出做大范围哦(单个文件最大５Ｍ)，请升级套餐'})

    return JsonResponse({'s':'s'})