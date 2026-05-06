from django.urls import path
from apps.accounts import views as acc_views

urlpatterns = [
    path('', acc_views.login_page, name='home'),
    path('login/', acc_views.login_page, name='login_page'),
    path('logout/', acc_views.web_logout_view, name='logout'),
    path('register/', acc_views.register_page, name='register_page'),
]

