from django import forms

from web.forms.bootstrap import BootsTrap
from web.models import Issues


class IssuesForm(BootsTrap, forms.ModelForm):
    """问题管理表单"""

    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            'assign': forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            'attention': forms.SelectMultiple(attrs={'class': "selectpicker", 'multiple data-actions-box': "true"}),
        }