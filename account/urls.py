from django.conf.urls import url
from account import views
from django.urls import path
app_name = "account"

urlpatterns = [
    path('',views.index, name="index"),  
    path('login/', views.Login, name='login'),
    path('signup/', views.Signup, name='signup'),
    path('logout/', views.Logout, name='logout'),
]