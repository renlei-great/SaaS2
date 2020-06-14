from django import forms

from web.forms.bootstrap import BootsTrap
from web.models import Issues, IssuesType, Module, ProjectUser


class IssuesForm(BootsTrap, forms.ModelForm):
    """问题管理表单"""

    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            'assign': forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            'attention': forms.SelectMultiple(attrs={'class': "selectpicker", 'multiple data-actions-box': "true"}),
            'module': forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            'parent': forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = request.tracer.project
        user = request.tracer.user

        # 查出当前项目下的所有问题类型
        issues_type = IssuesType.objects.filter(project=project).values_list('id', 'title')
        self.fields['issues_type'].choices = issues_type

        # 查出当前项目下的所有模块
        module_list = [("", "没有选择模块")]
        module = Module.objects.filter(project=project).values_list('id', 'title')
        module_list.extend(module)
        self.fields['module'].choices = module_list

        # 修改指派者和关注者
        account_list = [("", "没有选中"), (project.creator.id, project.creator.username)]
        pro_users = ProjectUser.objects.filter(project=project).values_list('user_id', 'user__username')
        account_list.extend(pro_users)
        self.fields['assign'].choices = account_list
        self.fields['attention'].choices = account_list

        # 修改父问题
        issues_list = [("", "没有选中"), ]
        issues = Issues.objects.filter(project=project).values_list('id', 'subject')
        issues_list.extend(issues)
        self.fields['parent'].choices = issues_list



