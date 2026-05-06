from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_home'),
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('ai/admin-agent/', views.admin_agent, name='admin_agent'),
    path('school/students/', views.students, name='admin_students'),
    path('school/attendance/', views.attendance, name='admin_attendance'),
    path('school/timetable/', views.timetable, name='admin_timetable'),
    path('logout/', views.logout_view, name='admin_logout'),
]
