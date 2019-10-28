from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User

urlpatterns = [
    path('', views.chat, name='chat'),
    path("register/", views.register, name="register"),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('search', views.search, name='search'),
    # path('uploadpic/', views.uploadpic,name='uploadpic')
    # path('<str:room_name>/', views.room, name='room')
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
