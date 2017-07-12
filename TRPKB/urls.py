"""TRPKB URL Configuration

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

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about_the_knowledgebase/', views.about_the_knowledgebase, name='about_the_knowledgebase'),
    url(r'^about_the_knowledge/', views.about_the_knowledge, name='about_the_knowledge'),
    url(r'^access_the_knowledge/', views.access_the_knowledge, name='access_the_knowledge'),
    url(r'^submit_the_knowledge/', views.submit_the_knowledge, name='submit_the_knowledge'),
    url(r'^news/', views.news, name='news'),
    url(r'^search_snp/', views.search_snp, name='search_snp'),
    url(r'^details_snp/(?P<research_id>\d+)/(?P<tumor_id>\d+)/(?P<variant_id>\d+)', views.details_snp, name='details_snp'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^import_data/', views.import_data, name='import_data'),
]
