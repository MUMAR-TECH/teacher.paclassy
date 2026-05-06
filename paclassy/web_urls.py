from django.urls import path
from apps.accounts import views as acc_views
from apps.dashboard import views as dash_views

urlpatterns = [
    path('', acc_views.login_page, name='home'),
    path('login/', acc_views.login_page, name='login_page'),
    path('register/', acc_views.register_page, name='register_page'),
    # Role-specific dashboards
    path('dashboard/teacher/', dash_views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', dash_views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', dash_views.admin_dashboard, name='admin_dashboard'),
    # Teacher-only AI tools
    path('ai/lesson-planner/', dash_views.lesson_planner_page, name='lesson_planner'),
    path('ai/assessment-generator/', dash_views.assessment_generator_page, name='assessment_generator'),
    path('ai/content-generator/', dash_views.content_generator_page, name='content_generator'),
    path('ai/teacher-agent/', dash_views.teacher_agent_page, name='teacher_agent'),
    # Student-only AI tools
    path('ai/tutor/', dash_views.ai_tutor_page, name='ai_tutor'),
    # Admin-only AI tools
    path('ai/admin-agent/', dash_views.admin_agent_page, name='admin_agent'),
    # School management
    path('school/attendance/', dash_views.attendance_page, name='attendance'),
    path('school/timetable/', dash_views.timetable_page, name='timetable'),
    path('school/students/', dash_views.students_page, name='students'),
]
