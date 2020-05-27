from django.shortcuts import render, reverse, redirect

from web.forms.wiki import WikiForm


def wiki(request, pro_id):
    """wiki首页显示"""
    return render(request, 'wiki.html')


def wiki_add(request, pro_id):
    if request.method == 'GET':
        wiki_form = WikiForm(request)
        return render(request, 'wiki_add.html', {'wiki_form': wiki_form})
    if request.method == 'POST':
        wiki_form = WikiForm(request.POST)

        if not wiki_form.is_valid():
            return render(request, 'wiki_add.html', {'wiki_form': wiki_form})

        wiki_form.instance.project_id = pro_id
        wiki_form.save()
        url = reverse('web:manage:wiki', kwargs={'pro_id': pro_id})

        return redirect(url)