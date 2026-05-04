from django.urls import path
from . import views

urlpatterns = [
    path('lesson-plans/', views.LessonPlanListCreateView.as_view(), name='lesson-plan-list'),
    path('lesson-plans/<int:pk>/', views.LessonPlanDetailView.as_view(), name='lesson-plan-detail'),
    path('assessments/', views.AssessmentListCreateView.as_view(), name='assessment-list'),
    path('assessments/<int:pk>/', views.AssessmentDetailView.as_view(), name='assessment-detail'),
    path('content/', views.ContentListCreateView.as_view(), name='content-list'),
    path('tutor/sessions/', views.TutorSessionListCreateView.as_view(), name='tutor-sessions'),
    path('tutor/sessions/<int:pk>/chat/', views.TutorChatView.as_view(), name='tutor-chat'),
]
