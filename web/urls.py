
from django.conf.urls import url
from web.views.account import register, send_sms

urlpatterns = [
    url(r'^register/$', register, name='register'),
    url(r'^send/', send_sms, name='send_sms')
]
