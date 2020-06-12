import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from sts.sts import Sts
from django.views.decorators.csrf import csrf_exempt

from web.models import FileManage
from web.forms.file import FileForm, FileAddForm
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
                parent=file_id).order_by('-file_cla')

            file = FileManage.objects.get(id=file_id)

            while file:
                files_list.append({'name': file.file_name, 'id': file.id})
                file = file.parent

        else:
            # 查询根文件和文件夹
            files = FileManage.objects.filter(project_id=pro_id, parent=None).order_by('-file_cla')

        file_form = FileForm(request)

        return render(request, 'file.html', {'files': files, 'file_form': file_form, 'files_list': files_list, 'file_id': file_id})

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


@csrf_exempt
def add_file(request, pro_id):
    """创建文件"""
    file_add_form = FileAddForm(request, data=request.POST)
    # 获取数据
    if not file_add_form.is_valid():
        # 验证失败
        return JsonResponse({'status': False, 'error': file_add_form.errors})
    # 数据校验通过
    # 获得真确字段，进行修改，然后在数据库中创建数据
    instance = file_add_form.cleaned_data
    instance.pop('etag')
    instance.update({
        'project': request.tracer.project,
        'file_cla': 1,
        'update_user': request.tracer.user,
    })
    data_dict = FileManage.objects.create(**instance)

    request.tracer.project.used_space += data_dict.file_size
    request.tracer.project.save()

    res = {
        'file_name': data_dict.file_name,
        'file_size': data_dict.file_size,
        'update_user': data_dict.update_user.username,
        'create_time': data_dict.create_time.strftime('%Y年%m月%d日 %H:%M'),
        'file_id': data_dict.id,
    }

    return JsonResponse({'status': True, 'res': res})


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
        # 先判断类型
        if file.file_cla == 2:
            files = FileManage.objects.filter(parent=file)
            # 文件夹
            for f in files:
                if f.file_cla == 2:
                    # 文件夹
                    file_list.append(f)
                else:
                    # 文件
                    file_size += f.file_size
                    key_list.append({'Key': f.key})
        else:
            # 文件
            file_size += file.file_size
            key_list.append({'Key': file.key})

    if key_list:  # 当有删除数据的时候执行
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
    project.save()

    # 删除文件或文件夹:删除时不能复制？
    FileManage.objects.get(id=pid, project=project, update_user=user).delete()

    # 成功返回
    return JsonResponse({'status': True})


# http://192.168.223.134:8000/web/manage/23/acquire/sts/
@csrf_exempt
def acquire_sts(request, pro_id):
    """前端获取临时凭证"""
    # 获取文件参数
    file_list = json.loads(request.body.decode())

    # 查询用户的套餐单文件最大的限制
    per_file_size = int(request.tracer.price_policy.per_file_size) * 1024 * 1024

    # 查询用户的套餐单项目最大的容量限制
    pro_file_space = int(request.tracer.price_policy.pro_space) * 1024 * 1024

    # 用户现在所用空间
    user_file_space = int(request.tracer.project.used_space)

    # 定义一个存放文件总需要的空间的
    file_num_size = 0

    # 便利每一个文件进行判断
    for file in file_list:
        print(file)
        # 判断单文件是否超出限制
        if int(file['file_size']) > per_file_size:
            return JsonResponse({'status': False, 'error': '单文件超出做大范围哦(单个文件最大５Ｍ)，请升级套餐'})
        # 累加总需空间
        file_num_size += int(file['file_size'])

    # 判断用户是否超出总空间
    if pro_file_space < user_file_space + file_num_size:
        return JsonResponse({'status': False, 'error': '项目存储容量超出最大范围哦，请升级套餐'})

    # 获取临时凭证
    res = cos_acquire_sts(request)

    return JsonResponse({'status': True, 'res': res})


# http://192.168.223.134:8000/web/manage/23/upload/sts/
@csrf_exempt
def upload_file(request, pro_id):
    """前端获取临时凭证"""
    #　获取要下载的文件id
    fid = request.GET.get('fid')

    # 查询要下载的文件对象
    file = FileManage.objects.get(
        id=fid,
        update_user=request.tracer.user,
        project=request.tracer.project
    )

    # 获取临时凭证
    client = create_cos()

    # 获取文件到本地
    response = client.get_object(
        Bucket='examplebucket-1250000000',
        Key='picture.jpg',
    )
    print(response['Body'])
    a = response['Body']



    return JsonResponse({
        'key': file.key,
        'bucket': request.tracer.project.bucket
    })