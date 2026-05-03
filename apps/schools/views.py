from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import School, Class
from .serializers import SchoolSerializer, ClassSerializer
from apps.accounts.permissions import IsSchoolAdmin, IsTeacherOrAdmin


class SchoolListCreateView(generics.ListCreateAPIView):
    serializer_class = SchoolSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return School.objects.all()
        if self.request.user.school:
            return School.objects.filter(id=self.request.user.school.id)
        return School.objects.none()


class SchoolDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return School.objects.all()
        if self.request.user.school:
            return School.objects.filter(id=self.request.user.school.id)
        return School.objects.none()


class ClassListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.school:
            return Class.objects.none()
        return Class.objects.filter(school=user.school)

    def perform_create(self, serializer):
        if not self.request.user.school:
            raise PermissionDenied('You must be associated with a school.')
        serializer.save(school=self.request.user.school)


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.school:
            return Class.objects.none()
        return Class.objects.filter(school=user.school)
