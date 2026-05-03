from django.urls import path
from . import views

urlpatterns = [
    path('', views.SchoolListCreateView.as_view(), name='school-list'),
    path('<int:pk>/', views.SchoolDetailView.as_view(), name='school-detail'),
    path('classes/', views.ClassListCreateView.as_view(), name='class-list'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class-detail'),
]
