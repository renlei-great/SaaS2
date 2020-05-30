
from django.conf.urls import url, include
from web.views.account import register, send_sms, login_sms, login, exit
from web.views.home import home_index
from web.views.project import project, asterisk
from web.views import manage, wiki

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
        url('(?P<pro_id>\d+)/dashboard', manage.dashboard, name='dashboard'),
        url('(?P<pro_id>\d+)/issues', manage.issues, name='issues'),
        url('(?P<pro_id>\d+)/statistics', manage.statistics, name='statistics'),

        url('(?P<pro_id>\d+)/wiki$', wiki.wiki, name='wiki'),
        url(r'(?P<pro_id>\d+)/wiki/add$', wiki.wiki_add, name='wiki_add'),
        url(r'(?P<pro_id>\d+)/wiki/catalog$', wiki.wiki_catalog, name='wiki_catalog'),
        url(r'(?P<pro_id>\d+)/wiki/del$', wiki.wiki_del, name='wiki_del'),
        url(r'(?P<pro_id>\d+)/wiki/edit$', wiki.wiki_edit, name='wiki_edit'),

        url('(?P<pro_id>\d+)/setting', manage.setting, name='setting'),
    ], namespace='manage')),
]
