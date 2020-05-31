import json
import uuid

from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from web.forms.wiki import WikiForm
from web.models import Wiki, Project
from utils.tencent.cos import create_cos


def wiki(request, pro_id):
    """wiki首页显示"""
    wiki_id = request.GET.get('wiki_id', None)
    print(wiki_id)
    try:
        wiki = Wiki.objects.filter(id=wiki_id, project_id = pro_id).first()
        return render(request, 'wiki.html', {'wiki': wiki})
    except Exception as e:
        print(e)
        return render(request, 'wiki.html')


def wiki_add(request, pro_id):
    if request.method == 'GET':
        wiki_form = WikiForm(request)

        return render(request, 'wiki_form.html', {'wiki_form': wiki_form})
    if request.method == 'POST':
        wiki_form = WikiForm(request, request.POST)

        if not wiki_form.is_valid():
            return render(request, 'wiki_form.html', {'wiki_form': wiki_form})

        if wiki_form.instance.parent:
            wiki_form.instance.depth = wiki_form.instance.parent.depth + 1
        else:
            wiki_form.instance.depth = 1

        wiki_form.instance.project_id = pro_id
        wiki_form.save()
        url = reverse('web:manage:wiki', kwargs={'pro_id': pro_id})

        return redirect(url)


def wiki_catalog(request, pro_id):
    """展示目录"""
    catas = Wiki.objects.filter(project_id=pro_id).order_by('depth', 'id').values('id', 'title', 'parent')
    return JsonResponse({'status': True, 'catas': list(catas)})


def wiki_del(request, pro_id):
    """删除文章"""
    wiki_id = request.GET.get('wiki_id', None)
    try:
        wiki_id = int(wiki_id)
        Wiki.objects.get(id=wiki_id).delete()

    except Exception as e:
        print(e)

    return redirect(reverse('web:manage:wiki', kwargs={'pro_id': pro_id}))


def wiki_edit(request, pro_id):
    """编辑文章"""
    try:
        wiki_id = request.GET.get('wiki_id')
        wiki_obj = Wiki.objects.get(project_id=pro_id, id=wiki_id)
    except Exception as e:
        print(e)
        # 如果没有此项目，跳转回wiki首页
        url = reverse('web:wiki', kwargs={'pro_id': pro_id})
        return redirect(url)

    if request.method == 'GET':
        """显示编辑页"""
        wiki_form = WikiForm(request, instance=wiki_obj)
        # 成进行返回
        return render(request, 'wiki_form.html', {'wiki_form': wiki_form})

    if request.method == 'POST':
        """提交编辑页"""
        wiki_form = WikiForm(request, data=request.POST, instance=wiki_obj)
        if wiki_form.is_valid():
            # 校验通过
            # 查看是否有父id
            if wiki_form.instance.parent:
                # 将深度加一
                wiki_form.instance.depth = wiki_form.instance.parent.depth + 1
            else:
                wiki_form.instance.depth = 1

            wiki_form.save()
            # 返回到文章页
            url = reverse('web:manage:wiki', kwargs={'pro_id': pro_id})
            url = url + '?wiki_id={}'.format(wiki_form.instance.id)

            return redirect(url)


@csrf_exempt
def wiki_upload(request, pro_id):
    """往cos上传文件"""
    res = {
        'success': 0,
        'message': None,
        'url': None,
    }

    files_obj = request.FILES.get('editormd-image-file')
    if not files_obj:
        res['message'] = '文件不存在'
        return JsonResponse(res)

    # 建立链接腾讯云对象
    client = create_cos(region='ap-nanjing')
    # pro = Project.objects.filter(id=pro_id).first()

    # 取出文件格式
    str_pre = files_obj.name.split('.')[-1]

    # 拼接存储的文件名
    file_name = f'pro_id-{pro_id}-user-id-{request.tracer.user.id}-{str(uuid.uuid4())[1:5]}.{str_pre}'
    client.upload_file_from_buffer(
        Bucket=request.tracer.project.bucket,
        Body=files_obj,
        Key=file_name,
        PartSize=1,
        MAXThread=10,
        EnableMD5=False
    )

    # 拼接文件URL
    # https://user-id-8-user-mobile-15561245051-552f-1302000219.cos.ap-nanjing.myqcloud.com/pro_id-19-user-id-8-a515.jpg
    url = f'https://{request.tracer.project.bucket}.cos.ap-nanjing.myqcloud.com/{file_name}'

    # 组织返回的数据
    res['success'] = 1
    res['url'] = url

    return JsonResponse(res)