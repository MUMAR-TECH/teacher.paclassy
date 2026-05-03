from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.AttendanceListCreateView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance-detail'),
    path('timetable/', views.TimetableListCreateView.as_view(), name='timetable-list'),
    path('timetable/<int:pk>/', views.TimetableDetailView.as_view(), name='timetable-detail'),
    path('report-cards/', views.ReportCardListCreateView.as_view(), name='report-card-list'),
]
