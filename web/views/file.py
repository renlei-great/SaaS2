from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from web.models import FileManage
from web.forms.file import FileForm


def file(request, pro_id):
    if request.method == 'GET':
        """显示文件管理首页"""
        file_id = request.GET.get('file_id', "")

        # 判断是否进入文件夹
        if file_id.isdecimal():
            # 进入了某一个文件夹
            files = FileManage.objects.filter(
                project_id=pro_id,
                update_user=request.tracer.user,
                parent=file_id)
        else:
            # 查询根文件和文件夹
            files = FileManage.objects.filter(project_id=pro_id, parent=None)

        file_form = FileForm(request)

        return render(request, 'file.html', {'files': files, 'file_form': file_form})

    if request.method == 'POST':
        """添加文件夹"""
        file_form = FileForm(request, request.POST)
        file_id = request.GET.get('file_id', "")

        if not file_form.is_valid():
            return JsonResponse({'status': False, 'error': file_form.errors})

        file_form.instance.project_id = pro_id
        file_form.instance.file_cla = 2
        file_form.instance.update_user = request.tracer.user
        if file_id.isdecimal():
            file_form.instance.parent_id = file_id

        file_form.save()

        return JsonResponse({'status': True})

def file_add(request, pro_id):
    file_form = FileForm(request, request.POST)
    file_id = request.POST.get('file_id')

    if not file_form.is_valid():
        return JsonResponse({'status': False, 'error': file_form.errors[0]})

    file_form.instance.project_id = pro_id
    file_form.instance.file_cla = 2
    file_form.instance.update_user = request.tracer.user
    if file_id.isdecimal():
        file_form.instance.parent=file_id

    file_form.save()

    return JsonResponse({'status': True})