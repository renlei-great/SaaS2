
from django.conf.urls import url, include

from web.views.account import register, send_sms, login_sms, login, exit
from web.views.home import home_index
from web.views.project import project, asterisk
from web.views import manage, wiki, file, vsetting, issues, dashboard, statistics
from utils.tencent import cos

urlpatterns = [
    url(r'^register/$', register, name='register'),
    url(r'^loginsms', login_sms, name='login_sms'),
    url(r'^login', login, name='login'),
    url(r'^index', home_index, name='index'),
    url(r'^exit', exit, name='exit'),

    url(r'^send/', send_sms, name='send_sms'),

    # 项目展示
    url(r'^project', project, name='project'),
    url(r'^asterisk/(?P<pro_type>\w+)/', asterisk, name='aster'),

    # 项目管理
    url(r'^manage/', include([
        # 统计
        url(r'(?P<pro_id>\d+)/statistics$', statistics.statistics, name='statistics'),  # 显示
        url(r'(?P<pro_id>\d+)/statistics/priority', statistics.statistics_priority, name='statistics_priority'),  # 显示饼状图
        url(r'(?P<pro_id>\d+)/statistics/project/user', statistics.statistics_project_user, name='statistics_project_user'),  # 显示人员工作情况图

        # wiki管理
        url(r'(?P<pro_id>\d+)/wiki$', wiki.wiki, name='wiki'),
        url(r'(?P<pro_id>\d+)/wiki/add$', wiki.wiki_add, name='wiki_add'),
        url(r'(?P<pro_id>\d+)/wiki/catalog$', wiki.wiki_catalog, name='wiki_catalog'),
        url(r'(?P<pro_id>\d+)/wiki/del$', wiki.wiki_del, name='wiki_del'),
        url(r'(?P<pro_id>\d+)/wiki/edit$', wiki.wiki_edit, name='wiki_edit'),
        url(r'(?P<pro_id>\d+)/wiki/upload$', wiki.wiki_upload, name='wiki_upload'),

        # 文件管理
        url(r'(?P<pro_id>\d+)/file$', file.file, name='file'),  # 显示，添加，编辑
        url(r'(?P<pro_id>\d+)/file/del$', file.file_del, name='file_del'),  # 删除
        url(r'(?P<pro_id>\d+)/add/file$', file.add_file, name='add_file'),  # 添加文件
        url(r'(?P<pro_id>\d+)/acquire/sts/', file.acquire_sts, name='acquire_sts'),  # 前段获取cos临时凭证
        url(r'(?P<pro_id>\d+)/upload/file/', file.upload_file, name='upload_file'),  # 前段获取cos临时凭证

        # 配置
        url(r'(?P<pro_id>\d+)/setting$', manage.setting, name='setting'),  # 我的资料
        url(r'(?P<pro_id>\d+)/setting/delete$', vsetting.del_setting, name='del_setting'),  # 删除项目

        # 问题
        url(r'(?P<pro_id>\d+)/issues$', issues.issues, name='issues'),  # 显示问题
        url(r'(?P<pro_id>\d+)/issues/invite/code$', issues.invite_code, name='invite_code'),  # 生成邀请码
        url(r'^(?P<pro_id>\d+)/add/user$', issues.add_user_pro, name='add_user_pro'),  # 给某个项目添加成员
        url(r'(?P<pro_id>\d+)/issues/(?P<iss_id>\d+)/detaile/$', issues.issues_detail, name='issues_detail'),  # 显示问题详情
        url(r'(?P<pro_id>\d+)/issues/(?P<iss_id>\d+)/detaile/operate$', issues.init_issues_operate, name='issues_operate'),  # 操作记录

        # 概览
        url(r'(?P<pro_id>\d+)/dashboard$', dashboard.dashboard, name='dashboard'),  # 概览显示
        url(r'(?P<pro_id>\d+)/issues/chart$', dashboard.issues_chart, name='issues_chart'),  # 概览图显示
    ], namespace='manage')),
]
