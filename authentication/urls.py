from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .serialization import MyTokenObtainPairView


app_name = 'authapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('activate/<uidb64>/<token>/', views.acct_activation, name='account_activation'),
    path('password_confirmation/', views.password_confirmation, name='password_confirmation'),
    path('password_reset_activation/<uidb64>/<token>/', views.password_reset_activation, name='password_reset_activation'),
]
