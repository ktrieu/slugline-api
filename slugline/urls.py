"""slugline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.shortcuts import render

import common.views
import content.urls
import content.views
import user.views

urlpatterns = [
    path('', common.views.HomeView.as_view(), name='home'),

    path('api/', include(content.urls)),

    path('issues/', content.views.IssuesList.as_view(), name='issues'),
    path('issues/<int:volume>/<int:issue>/', content.views.IssueView.as_view(), name='issue'),

    path('articles/<int:id>/<slug:slug>/', content.views.ArticleView.as_view(), name='article'),
    path('articles/<int:id>/edit', content.views.ArticleEditView.as_view(), name='article_edit'),
    

    path('login/', user.views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dash/', user.views.DashView.as_view(), name='dash'),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = common.views.page_not_found
