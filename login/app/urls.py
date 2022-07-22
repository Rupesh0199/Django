from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('menu', views.menu, name='menu'),
    path('search', views.search, name='search'),
    path('userinfo', views.userInfo, name='userInfo'),
    path('uploadfile', views.uploadfile, name='uploadfile'),
    path('adduser', views.adduser, name='adduser'),
    path('deleteuser/<str:id>', views.deleteuser, name='delete'),
    path('logout', views.logout, name='logout'),
]
