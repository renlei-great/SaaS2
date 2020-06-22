from django import forms
from django.forms.fields import ValidationError

from web.forms.bootstrap import BootsTrap
from web.models import Issues, IssuesType, Module, ProjectUser
from web.models import IssuesReply, ProjectInvite

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
        account_list.pop(0)

        self.fields['attention'].choices = account_list

        # 修改父问题
        issues_list = [("", "没有选中"), ]
        issues = Issues.objects.filter(project=project).values_list('id', 'subject')
        issues_list.extend(issues)
        self.fields['parent'].choices = issues_list


class IssuesReplyForm(BootsTrap, forms.ModelForm):
    """提交回复或消息变更表单"""
    class Meta:
        model = IssuesReply
        fields = ['reply_type', 'content']


class IssuesProjectInvite(BootsTrap, forms.Form):
    """验证码做表单验证"""
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = forms.ChoiceField(label='有效期', choices=period_choices)
    count = forms.IntegerField(label='限制数量', help_text='空表示无数量限制', required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_count(self):
        count = self.cleaned_data.get('count', '')
        if not count:
            count = int(self.request.tracer.price_policy.pro_member) - 1

        if int(count) > int(self.request.tracer.price_policy.pro_member) - 1:
            raise ValidationError(f'项目最多可以邀请{int(self.request.tracer.price_policy.pro_member) - 1} 人，请升级套餐')

        return count



