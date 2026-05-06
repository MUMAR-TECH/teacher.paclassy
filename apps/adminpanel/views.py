from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render

from apps.accounts.decorators import role_required


@role_required('admin')
def dashboard(request):
    return render(request, 'adminpanel/dashboard.html')


@role_required('admin')
def admin_agent(request):
    return render(request, 'adminpanel/admin_agent.html')


@role_required('admin')
def students(request):
    return render(request, 'adminpanel/students.html')


@role_required('admin')
def attendance(request):
    return render(request, 'adminpanel/attendance.html')


@role_required('admin')
def timetable(request):
    return render(request, 'adminpanel/timetable.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')
