from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'account'

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.user_login, name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('register', views.register, name='register'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('account', views.account, name='account'),
    path('account/get-otp', views.get_otp, name='get-otp'),
    path('subscription', views.subscription, name='subscription'),
    path('reminder', views.set_reminder, name='set-reminder'),
    path('waiting', views.waiting_list, name='waiting-list'),
    path('informing', views.inform_report, name='informing'),
    path('payments', views.payments_report, name='payments'),
    path('pay/request', views.send_request, name='pay_request'),
    path('pay/verify', views.pay_verify, name='pay_verify'),
]
