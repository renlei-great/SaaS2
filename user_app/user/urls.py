
from django.conf.urls import url, include

from user_app.user import views

urlpatterns = [
    url(r'^login', views.login),
    url(r'^register', views.register),


    url(r'^project/', include('user_app.project.urls', namespace='project')),

    url(r'^send', views.send_sms),
]
