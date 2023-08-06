from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^prepare_hash$', views.prepare_hash, name='prepare_hash'),
    url(r'^callback$', views.callback, name='callback'),
]
