from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('upload_image', views.upload_image, name='upload_image'),
    path('getlist', views.getlist, name='getlist'),
    path('detail/<str:config_name>', views.detail, name='detail'),
    path('delete/<str:config_name>', views.delete, name='delete'),
    path('edit/<str:config_name>', views.edit, name='edit'),
    path('select/<str:config_name>', views.select, name='select'),
    path('select/<str:config_name>/<str:filename>/<int:pp>', views.select_demo, name='select_demo'),
    #path('upload_json', views.upload_json, name='upload_json'),

]
