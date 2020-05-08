
from django.conf.urls import url
from web.views.account import register

urlpatterns = [
    url(r'^register/$', register, name='register'),
]
