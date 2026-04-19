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
    path('my-orders/', views.my_orders, name='my_orders'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('invoice/<int:order_id>/', views.invoice_pdf, name='invoice_pdf'),
    
    


]


