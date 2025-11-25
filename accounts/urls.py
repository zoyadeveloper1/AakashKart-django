from django.urls import path
from . import views

urlpatterns = [

    # Registration
    path('register/', views.register, name='register'),

    # Login / Logout
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Activate Account
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Forgot / Reset Password
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),

    path('signup/', views.signup, name='signup'),
]
