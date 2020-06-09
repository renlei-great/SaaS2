from django import forms
from django.core.validators import ValidationError
from qcloud_cos.cos_exception import CosServiceError

from web.forms.bootstrap import BootsTrap
from web.models import FileManage
from utils.tencent.cos import create_cos


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
    etag = forms.CharField(label='ETag')

    class Meta:
        model = FileManage
        fields=['file_name', 'file_size', 'key', 'file_path', 'parent']

    def __init__(self, request, *args, **kwargs):
        super(FileAddForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_parent(self):
        return self.cleaned_data.get('parent', None)

    def clean_file_path(self):
        file_path = self.cleaned_data['file_path']
        return f'http"//{file_path}'

    def clean(self):
        """验证用户是否上传到了cos"""
        # 获取数据
        etag = self.cleaned_data['etag']
        key = self.cleaned_data['key']
        size = self.cleaned_data['file_size']

        client = create_cos()

        try:
            res = client.head_object(self.request.tracer.project.bucket, key)
        except CosServiceError as e:
            self.add_error("key", '文件不存在')
            return self.cleaned_data

        if etag != res.get('ETag'):
            self.add_error("eatg", '上传有误')
            return self.cleaned_data

        if int(res.get('Content-Length')) != int(size):
            self.add_error("file_size", '文件大小有误')
            return self.cleaned_data

        return self.cleaned_data