from django.shortcuts import render, redirect, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from base64 import urlsafe_b64decode, urlsafe_b64encode
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib import messages
from .utils import generate_token
from django.conf import settings
from django.views.generic import View
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError

@api_view(['GET'])
def index(request):
    routes = [
        {
            'route': 'auth/login/',
            'description': 'Login page',
        },
        {
            'route': 'auth/logout/',
            'description': 'Logout page',
        },
        {
            'route': 'auth/signup/',
            'description': 'Signup page',
        },
        {
            'route': 'auth/token/',
            'description': 'Get token',
        },
        {
            'route': 'auth/token/refresh/',
            'description': 'Refresh token',
        },
    ]

    return Response(routes)

# Create your views here.
def login_view(request):
    return render(request, 'authentication/login.html')

def logout_view(request):
    return render(request, 'authentication/logout.html')

@api_view(['GET'])
def acct_activation(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account Activated')
        return redirect('authapp:login')
    else:
        return HttpResponse('Activation link is invalid!')

@api_view(['GET'])
def password_reset_activation(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user is not None and generate_token.check_token(user, token):
        return render(request, 'authentication/password_reset_page.html', context={'uid64': uidb64,'token': token})
    else:
        return HttpResponse('Activation link is invalid!')

@api_view(['POST'])
def password_confirmation(request):
    try:
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        uid64 = request.POST.get('uid64')
        token = request.POST.get('token')
        print(f'passowrd: {password}')
        print(f'confirm_password: {confirm_password}')
        print(f'uidb64: {uid64}')
        print(f'token: {token}')
        if password == confirm_password:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
            print(f'user: {user.username}')
            if user is not None and generate_token.check_token(user, token):
                user.set_password(password)
                user.save()
                messages.success(request, 'Password Reset Successfully')
                return redirect('authapp:login')
            else: 
                messages.error(request, 'Token Invalid Please Try Again.')
                return redirect('authapp:login')
        else:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/password_reset_page.html', context={'uid64': uid64,'token': token})
    except Exception as identifier:
        messages.error(request, 'Something Went Wrong Please Try Again.')
        return redirect('authapp:login')

class PasswordReset(View):
    def get(self, request):
        return render(request, 'authentication/password_reset.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            subject = 'Password Reset Request'
            message = render_to_string('authentication/password_reset_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            print(f'Link {message}')

            email = EmailMessage(subject, message, to=[email])
            email.send()
            messages.success(request, 'Password reset link has been sent to your email')
            return redirect('authapp:login')
        except Exception as identifier:
            messages.error(request, 'Email does not exist')
            return render(request, 'authentication/password_reset.html')
        
class SignUpView(View):
    def get(self, request):
        return render(request, 'authentication/signup.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        conf_password = request.POST.get('confirm_password')
        if password != conf_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/signup.html')
        try:
            if User.objects.get(username=email):
                messages.error(request, 'Email Already Exists')
                return render(request, 'authentication/signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(username=email, password=password, email=email)
        user.is_active = False
        user.save()

        email_subject = 'Account Activation'
        message = render_to_string('authentication/acct_activation.html', {
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })

        print(f'Activation Link: {message}')

        email_message = EmailMessage(
            email_subject, message, settings.EMAIL_HOST_USER, [email]
        )
        email_message.send()
        messages.success(request, 'Account Created, Please check your email to activate your account')
        return redirect('authapp:login')
