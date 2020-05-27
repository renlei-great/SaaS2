from django import forms

from web.models import Wiki
from web.forms.bootstrap import BootsTrap


class WikiForm(BootsTrap, forms.ModelForm):
    """wiki提交"""
    class Meta:
        model = Wiki
        exclude = ['project']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pros = Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        tal_pros = [('', '请选择')]
        tal_pros.extend(pros)
        print(tal_pros)
        self.fields['parent'].choices = tal_pros
        pass