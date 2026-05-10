from django.urls import path
from . import views

urlpatterns = [
    path('lesson-plans/', views.LessonPlanListCreateView.as_view(), name='lesson-plan-list'),
    path('lesson-plans/<int:pk>/', views.LessonPlanDetailView.as_view(), name='lesson-plan-detail'),
    path('lesson-plans/<int:pk>/download/<str:fmt>/', views.LessonPlanDownloadView.as_view(), name='lesson-plan-download'),
    path('assessments/', views.AssessmentListCreateView.as_view(), name='assessment-list'),
    path('assessments/<int:pk>/', views.AssessmentDetailView.as_view(), name='assessment-detail'),
    path('content/', views.ContentListCreateView.as_view(), name='content-list'),
    # Student AI Tutor
    path('tutor/sessions/', views.TutorSessionListCreateView.as_view(), name='tutor-sessions'),
    path('tutor/sessions/<int:pk>/chat/', views.TutorChatView.as_view(), name='tutor-chat'),
    # Teacher AI Agent
    path('teacher-agent/sessions/', views.TeacherAgentSessionListCreateView.as_view(), name='teacher-agent-sessions'),
    path('teacher-agent/sessions/<int:pk>/chat/', views.TeacherAgentChatView.as_view(), name='teacher-agent-chat'),
    # Admin AI Agent
    path('admin-agent/sessions/', views.AdminAgentSessionListCreateView.as_view(), name='admin-agent-sessions'),
    path('admin-agent/sessions/<int:pk>/chat/', views.AdminAgentChatView.as_view(), name='admin-agent-chat'),
]
