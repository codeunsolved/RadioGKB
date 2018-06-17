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
from django.conf import settings
from django.conf.urls import url, include, static
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^help$', views.help, name='help'),
    url(r'^download$', views.download, name='download'),
    url(r'^submit$', views.submit, name='submit'),
    url(r'^submit/query', views.submit_query, name='submit_query'),
    url(r'^submit/add', views.submit_add, name='submit_add'),
    url(r'^news/', views.news, name='news'),
    url(r'^profile', views.profile, name='profile'),
    url(r'^snp/add/(?P<submit_id>\w+)', views.snp_add, name='snp_add'),
    url(r'^exp/add/(?P<submit_id>\w+)', views.exp_add, name='exp_add'),
    url(r'^snp/search', views.snp_search, name='snp_search'),
    url(r'^exp/search', views.exp_search, name='exp_search'),
    url(r'^snp/details/(?P<research_id>\d+)/(?P<tumor_id>\d+)/(?P<variant_id>\d+)', views.snp_details, name='snp_details'),
    url(r'^exp/details/(?P<research_id>\d+)/(?P<tumor_id>\d+)/(?P<gene_id>\d+)', views.exp_details, name='exp_details'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^import_snp/', views.import_snp, name='import_snp'),
    url(r'^import_exp/', views.import_exp, name='import_exp'),
    url(r'^locale$', views.view_locale),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
