from django import forms
from mdeditor.fields import MDTextFormField

from web.models import Wiki
from web.forms.bootstrap import BootsTrap


class TextForm(forms.Form):
    name = forms.CharField()
    age = forms.IntegerField()
    content = MDTextFormField()


class WikiForm(BootsTrap, forms.ModelForm):
    """wiki提交"""

    class Meta:
        model = Wiki
        exclude = ['project', 'depth']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pros = Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        tal_pros = [('', '请选择')]
        tal_pros.extend(pros)
        self.fields['parent'].choices = tal_pros