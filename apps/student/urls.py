from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='student_home'),
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('ai/tutor/', views.ai_tutor, name='ai_tutor'),
    path('logout/', views.logout_view, name='student_logout'),
]
