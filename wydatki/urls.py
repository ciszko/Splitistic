from django.urls import path, include
from . import views
from rest_framework import routers
from django.conf.urls import url, include


router = routers.DefaultRouter()
router.register('zakup', views.ZakupView)
router.register('uzytkownik', views.UzytkownikView)

urlpatterns = [
    path('', include(router.urls)),
    url(r'^graph/$', views.GraphView.as_view()),
    path('users/', views.UserList.as_view(), name='users'),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('users/add/', views.UserCreate.as_view()),
    path('', include('rest_framework.urls')),
    path('users/changepassword/', views.ChangePasswordView.as_view()),
    path('users/changeusername/', views.ChangeUsername.as_view()),
    ]