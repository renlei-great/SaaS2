
from django.conf.urls import url
from web.views.account import register, send_sms, login_sms, login, exit
from web.views.home import home_index
from web.views.project import project, asterisk

urlpatterns = [
    url(r'^register/$', register, name='register'),
    url(r'^loginsms', login_sms, name='login_sms'),
    url(r'^login', login, name='login'),
    url(r'^index', home_index, name='index'),
    url(r'^exit', exit, name='exit'),

    url(r'^send/', send_sms, name='send_sms'),

    # 项目管理
    url(r'^project', project, name='project'),
    url(r'^asterisk/(?P<pro_type>\w+)/', asterisk, name='aster')

]
