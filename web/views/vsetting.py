from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse

from utils.tencent.cos import create_cos
from web.models import Project


def del_setting(request, pro_id):
    """删除项目"""
    if request.method == 'GET':
        return render(request, 'del_setting.html')

    pro_name = request.POST.get('pro_name')

    # 校验删除项目的数据
    if not pro_name:
        return JsonResponse({'status': False, 'error': '请输入项目名'})

    if pro_name != request.tracer.project.project_name:
        # 项目名错误
        return JsonResponse({'status': False, 'error': '项目名错误'})

    # 验证通过，开始执行操作删除项目
    # 删除桶中的所有项目－　删除桶的碎片文件 - 删除桶
    # 创建一个cos对象
    client = create_cos()
    # response = client.list_objects(request.tracer.project.bucket)

    list_file_key = []
    bucket = request.tracer.project.bucket
    while True:
        # 查出桶的所有文件- 每次最大取１０００个
        response = client.list_objects(bucket)

        if not response.get('Contents'):
            break

        # 获取查询出来的文件对象
        files = response.get('Contents')
        for file in files:
            list_file_key.append({'Key': file['Key']})

        if response['IsTruncated'] == 'false':
            break

    # 删除桶中的所有文件
    objects = {
                "Quiet": "true",
                "Object": list_file_key
            }
    if list_file_key:
        client.delete_objects(bucket, objects)

    # 清除桶中的碎片文件
    while True:
        mul_list = client.list_multipart_uploads(bucket)
        uploads = mul_list.get('Upload')

        if not uploads:
            break

        for load in uploads:
            # 单个进行删除
            client.abort_multipart_upload(bucket, load['Key'], load['UploadId'])

        if uploads['IsTruncated'] == 'false':
            break

    # 删除数据库中的项目
    Project.objects.get(id=int(pro_id), project_name=pro_name, creator=request.tracer.user).delete()
    client.delete_bucket(bucket)

    return JsonResponse({'status': True, 'url': reverse('web:project')})