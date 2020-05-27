from django import forms
from django.core.validators import ValidationError

from web.models import Project
from web.forms.bootstrap import BootsTrap
from web.forms.widgets import ColorRadioSelect


class ProjectForm(BootsTrap, forms.ModelForm):
    bootstrap_class_exclude = ['color']
    """创建项目表单"""

    class Meta:
        model = Project
        fields = ['project_name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect,
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_project_name(self):
        name = self.cleaned_data['project_name']
        # 验证用户创建的项目是否重名
        user_pros = Project.objects.filter(creator=self.request.tracer.user)
        is_name = user_pros.filter(project_name=name).exists()
        if is_name:
            raise ValidationError('该项目已经创建')
        # 验证用户创建的项目个数是否还够
        pro_count = user_pros.count()
        if pro_count > self.request.tracer.price_policy.pro_num:
            raise ValidationError('已达到最大项目数，请升级套餐')

        return name
