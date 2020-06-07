from django import forms
from django.core.validators import ValidationError

from web.forms.bootstrap import BootsTrap
from web.models import FileManage


class FileForm(BootsTrap, forms.ModelForm):
    """文件表单"""
    class Meta:
        model = FileManage
        fields = ['file_name']

    def __init__(self, request, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_file_name(self):
        """验证name是否重名"""
        name = self.cleaned_data['file_name']
        file_id = self.request.GET.get('file_id', "")

        # 查询该文件夹下的所有文件或目录
        file_obj = FileManage.objects.filter(
            project=self.request.tracer.project,
            update_user=self.request.tracer.user)

        if file_id.isdecimal():
            file_obj = file_obj.filter(parent=file_id, file_name=name).first()
        else:
            file_obj = file_obj.filter(parent=None, file_name=name).first()

        if file_obj:
            raise ValidationError('文件已存在')

        return name


class FileAddForm(BootsTrap, forms.ModelForm):
    """添加文件表单"""
    class Meta:
        model = FileManage
        fields=['file_name', 'file_size', ]