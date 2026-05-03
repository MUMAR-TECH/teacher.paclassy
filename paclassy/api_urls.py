from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.accounts.urls')),
    path('schools/', include('apps.schools.urls')),
    path('ai/', include('apps.ai_engine.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('school-mgmt/', include('apps.school_mgmt.urls')),
    path('analytics/', include('apps.analytics.urls')),
]
