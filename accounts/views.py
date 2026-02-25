from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .utils import send_reset_email
from .forms import RegistrationForm, LoginForm
from .models import Account
import requests


# ---------------------------------------------------
# CUSTOM LOGIN VIEW
# ---------------------------------------------------
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, f"Welcome {form.get_user().first_name} 👋")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password ❌")
        return super().form_invalid(form)


# ---------------------------------------------------
# REGISTRATION
# ---------------------------------------------------
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.split("@")[0]
            user.is_active = False
            user.save()

            # Activation Email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'

            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            messages.success(request, "We sent you an activation email ✔")
            return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully ✔")
    return redirect('login')


# ---------------------------------------------------
# ACTIVATE ACCOUNT
# ---------------------------------------------------
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account is activated 🎉")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid ❌")
        return redirect('register')


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


# ---------------------------------------------------
# FORGOT PASSWORD - SEND RESET EMAIL
# ---------------------------------------------------
def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            if not user.is_active:
                messages.error(request, "This account is not active ❌")
                return redirect('forgotpassword')

            # UID + Token
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_url = request.build_absolute_uri(
                reverse('resetpassword_validate', kwargs={'uidb64': uidb64, 'token': token})
            )

            # Send Email
            send_reset_email(user, reset_url)

            messages.success(request, "Password reset email sent ✔")
            return redirect('login')

        messages.error(request, "Account does not exist ❌")
        return redirect('forgotpassword')

    return render(request, 'accounts/forgotpassword.html')


# ---------------------------------------------------
# VALIDATE RESET TOKEN
# ---------------------------------------------------
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Reset link verified ✔ Create new password")
        return redirect('resetpassword')

    messages.error(request, "The link has expired or is invalid ❌")
    return redirect('forgotpassword')


# ---------------------------------------------------
# SET NEW PASSWORD
# ---------------------------------------------------
def resetpassword(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)

            user.set_password(password)
            user.save()

            messages.success(request, "Password reset successful ✔")
            return redirect('login')

        messages.error(request, "Passwords do not match ❌")
        return redirect('resetpassword')

    return render(request, 'accounts/resetpassword.html')


# ---------------------------------------------------
# Simple Signup Page
# ---------------------------------------------------
def signup(request):
    return render(request, 'accounts/signup.html')
