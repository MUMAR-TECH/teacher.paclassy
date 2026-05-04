from django.urls import path
from . import views

urlpatterns = [
    path('submissions/', views.SubmissionListCreateView.as_view(), name='submission-list'),
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission-detail'),
]
