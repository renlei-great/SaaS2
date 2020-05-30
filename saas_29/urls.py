"""saas_29 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from saas_29 import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('user_app.user.urls', namespace='user')),  # 测试走的路由
    url(r'^web/', include('web.urls', namespace='web')),  # 正式走的路由

    url(r'^captcha/', include('captcha.urls')),  # 验证码
    url(r'mdeditor/', include('mdeditor.urls')),  # 富文本

]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
