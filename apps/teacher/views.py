from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render

from apps.accounts.decorators import role_required


@role_required('teacher')
def dashboard(request):
    return render(request, 'teacher/dashboard.html')


@role_required('teacher')
def lesson_planner(request):
    return render(request, 'teacher/lesson_planner.html')


@role_required('teacher')
def assessment_generator(request):
    return render(request, 'teacher/assessment_generator.html')


@role_required('teacher')
def content_generator(request):
    return render(request, 'teacher/content_generator.html')


@role_required('teacher')
def teacher_agent(request):
    return render(request, 'teacher/teacher_agent.html')


@role_required('teacher')
def attendance(request):
    return render(request, 'teacher/attendance.html')


@role_required('teacher')
def timetable(request):
    return render(request, 'teacher/timetable.html')


@role_required('teacher')
def students(request):
    return render(request, 'teacher/students.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')
