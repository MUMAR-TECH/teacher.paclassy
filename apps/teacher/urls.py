from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='teacher_home'),
    path('dashboard/', views.dashboard, name='teacher_dashboard'),
    path('ai/lesson-planner/', views.lesson_planner, name='lesson_planner'),
    path('ai/assessment-generator/', views.assessment_generator, name='assessment_generator'),
    path('ai/content-generator/', views.content_generator, name='content_generator'),
    path('ai/teacher-agent/', views.teacher_agent, name='teacher_agent'),
    path('school/attendance/', views.attendance, name='teacher_attendance'),
    path('school/timetable/', views.timetable, name='teacher_timetable'),
    path('school/students/', views.students, name='teacher_students'),
    path('logout/', views.logout_view, name='teacher_logout'),
]
