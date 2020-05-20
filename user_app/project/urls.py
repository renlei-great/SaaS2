
from django.conf.urls import url

from user_app.project.views import project, asterisk

urlpatterns = [
    url(r'^project', project, name='project'),
    url(r'^asterisk', asterisk, name='aster')
]
