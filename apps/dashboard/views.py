from django.shortcuts import render


def teacher_dashboard(request):
    return render(request, 'dashboard/teacher.html')


def student_dashboard(request):
    return render(request, 'dashboard/student.html')


def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')


def lesson_planner_page(request):
    return render(request, 'ai_engine/lesson_planner.html')


def assessment_generator_page(request):
    return render(request, 'ai_engine/assessment_generator.html')


def content_generator_page(request):
    return render(request, 'ai_engine/content_generator.html')


def ai_tutor_page(request):
    return render(request, 'ai_engine/ai_tutor.html')


def attendance_page(request):
    return render(request, 'school_mgmt/attendance.html')


def timetable_page(request):
    return render(request, 'school_mgmt/timetable.html')


def students_page(request):
    return render(request, 'school_mgmt/students.html')
