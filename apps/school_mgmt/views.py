from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from .models import AttendanceRecord, TimetableEntry, ReportCard
from .serializers import AttendanceRecordSerializer, TimetableEntrySerializer, ReportCardSerializer
from apps.accounts.permissions import IsTeacherOrAdmin
from apps.ai_engine.services import ai_service


class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.school:
            return AttendanceRecord.objects.none()
        qs = AttendanceRecord.objects.filter(school=user.school)
        date = self.request.query_params.get('date')
        class_id = self.request.query_params.get('class')
        if date:
            qs = qs.filter(date=date)
        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        return qs

    def perform_create(self, serializer):
        if not self.request.user.school:
            raise PermissionDenied('You must be associated with a school.')
        serializer.save(school=self.request.user.school)


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.school:
            return AttendanceRecord.objects.none()
        return AttendanceRecord.objects.filter(school=user.school)


class TimetableListCreateView(generics.ListCreateAPIView):
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.school:
            return TimetableEntry.objects.none()
        qs = TimetableEntry.objects.filter(school=user.school)
        class_id = self.request.query_params.get('class')
        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        return qs

    def perform_create(self, serializer):
        if not self.request.user.school:
            raise PermissionDenied('You must be associated with a school.')
        serializer.save(school=self.request.user.school)


class TimetableDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        if not self.request.user.school:
            return TimetableEntry.objects.none()
        return TimetableEntry.objects.filter(school=self.request.user.school)


class ReportCardListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.school:
            return Response([])
        if user.role == 'student':
            reports = ReportCard.objects.filter(student=user, school=user.school)
        else:
            reports = ReportCard.objects.filter(school=user.school)
        serializer = ReportCardSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.school:
            raise PermissionDenied('You must be associated with a school.')
        serializer = ReportCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.validated_data['student']
        student_name = f"{student.first_name} {student.last_name}".strip() or student.username
        ai_summary = ai_service.generate_report_summary(
            student_name=student_name,
            grades_data=serializer.validated_data.get('grades', {}),
        )
        report = serializer.save(school=request.user.school, ai_summary=ai_summary)
        return Response(ReportCardSerializer(report).data, status=status.HTTP_201_CREATED)
