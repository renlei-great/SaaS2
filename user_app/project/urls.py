
from django.conf.urls import url

from user_app.project.views import project, asterisk, wiki, issues
from user_app.project import views

urlpatterns = (
    url(r'^project', project, name='project'),
    url(r'^asterisk', asterisk, name='aster'),
    url(r'^wiki$', wiki, name='wiki'),
    url(r'^wiki/sts', views.wiki_st, name='wiki_sts'),
    url(r'^isseus/(?P<pro_id>\w+)$', views.issues, name='isseus'),

    url(r'^test/$', views.test, name='test'),

)
