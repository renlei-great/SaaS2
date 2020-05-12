
from django.conf.urls import url
from web.views.account import register, send_sms, login_sms

urlpatterns = [
    url(r'^register/$', register, name='register'),
    url(r'^loginsms', login_sms, name='login_sms'),

    url(r'^send/', send_sms, name='send_sms'),

]
