import json

from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse

from web.forms.wiki import WikiForm
from web.models import Wiki


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
