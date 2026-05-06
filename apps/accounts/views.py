from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


# ---------------------------------------------------------------------------
# JWT / REST API views (used by the API endpoints)
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response({
            'user': UserSerializer(data['user']).data,
            'access': data['access'],
            'refresh': data['refresh'],
        })


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out successfully.'})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# Web / session-based views
# ---------------------------------------------------------------------------

def _redirect_by_role(request, role):
    """Redirect to the correct role section dashboard."""
    role_map = {
        'teacher': '/teacher/dashboard/',
        'student': '/student/dashboard/',
        'admin': '/admin_panel/dashboard/',
    }
    return HttpResponseRedirect(role_map.get(role, '/login/'))


def login_page(request):
    """Session-based web login.  Redirects to the correct role subdomain on success."""
    if request.user.is_authenticated:
        return _redirect_by_role(request, request.user.role)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return _redirect_by_role(request, user.role)
        error = 'Invalid username or password. Please try again.'

    return render(request, 'accounts/login.html', {'error': error})


def register_page(request):
    return render(request, 'accounts/register.html')


def web_logout_view(request):
    """Logs the user out of the Django session and redirects to login."""
    logout(request)
    return redirect('login_page')

