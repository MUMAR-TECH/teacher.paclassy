from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('paclassy.api_urls')),
    path('teacher/', include('apps.teacher.urls')),
    path('student/', include('apps.student.urls')),
    path('admin_panel/', include('apps.adminpanel.urls')),
    path('', include('paclassy.web_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
