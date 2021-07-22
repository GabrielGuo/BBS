"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

# from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from BBS import settings
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.index),
    re_path('^$', views.index),
    path('index/', views.index),
    path('login/', views.login),
    path('get_code/', views.get_code),
    path('register/', views.register),
    path('logout/', views.logout),
    # 点赞路由
    path('diggit/', views.diggit),
    # 评论提交
    path('commit/', views.commit),

    # 后台管理首页
    path('backend/', views.home_backend),
    # 后台 添加文章
    path('add_article/', views.add_article),
    # 上传图片的路径
    path('uploadimg/', views.uploadimg),


    # 开启media的口子
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    re_path(r'^media/(?P<path>.*)', serve, kwargs={"document_root": settings.MEDIA_ROOT}),
    # path('media/(?P<path>.*)', serve, kwargs={'document_root': settings.MEDIA_ROOT})

    # re_path(r'^(?P<username>\w+)/tag/(?P<id>)\d+ $', views.site_page),
    # re_path(r'^(?P<username>\w+)/category/(?P<id>)\d+ $', views.site_page),
    # re_path(r'^(?P<username>\w+)/archive/(?P<id>)\d+ $', views.site_page),
    # 上面三条合成下面一条
    # re_path(r'^(?P<username>\w+)/(?P<condition>\w+)/(?P<param>)\w+ $', views.site_page),
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)$', views.site_page),

    # 文章详情页面
    re_path(r'^(?P<username>\w+)/article/(?P<pk>\d+)$', views.article_detail),


    # 一定注意要放到最后，才匹配该url
    re_path(r'^(?P<username>\w+)$', views.site_page),

]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# 配置图片文件url转发


