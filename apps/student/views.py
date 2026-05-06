from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render

from apps.accounts.decorators import role_required


@role_required('student')
def dashboard(request):
    return render(request, 'student/dashboard.html')


@role_required('student')
def ai_tutor(request):
    return render(request, 'student/ai_tutor.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')
