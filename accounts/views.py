from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string, get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse

from xhtml2pdf import pisa

from .utils import send_reset_email
from .forms import RegistrationForm, LoginForm
from .models import Account, Address

from orders.models import Order, OrderProduct


# ---------------------------------------------------
# LOGIN
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
# REGISTER
# ---------------------------------------------------
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.split("@")[0]
            user.is_active = False
            user.save()

            current_site = get_current_site(request)

            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            email = EmailMessage(
                'Activate your account',
                message,
                to=[user.email]
            )
            email.send()

            messages.success(request, "Activation email sent ✔")
            return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ---------------------------------------------------
# SIGNUP (alias)
# ---------------------------------------------------
def signup(request):
    return register(request)


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully ✔")
    return redirect('login')


# ---------------------------------------------------
# ACTIVATE
# ---------------------------------------------------
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated 🎉")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link ❌")
        return redirect('register')


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@login_required(login_url='login')
def dashboard(request):
    orders_count = Order.objects.filter(user=request.user).count()
    return render(request, 'accounts/dashboard.html', {'orders_count': orders_count})


# ---------------------------------------------------
# MY ORDERS
# ---------------------------------------------------
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


# ---------------------------------------------------
# EDIT PROFILE
# ---------------------------------------------------
@login_required
def edit_profile(request):
    user = request.user
    address, _ = Address.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()

        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect('edit_profile')

    return render(request, 'accounts/edit_profile.html', {'user': user, 'address': address})


# ---------------------------------------------------
# CHANGE PASSWORD
# ---------------------------------------------------
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully ✅")
            return redirect('change_password')
        else:
            messages.error(request, "Check your input ❌")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


# ---------------------------------------------------
# ORDER DETAIL
# ---------------------------------------------------
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_products = OrderProduct.objects.filter(order=order)

    for item in order_products:
        item.total = item.quantity * (item.product_price or item.product.price)

    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'order_products': order_products,
    })


# ---------------------------------------------------
# INVOICE PDF
# ---------------------------------------------------
@login_required
def invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_products = OrderProduct.objects.filter(order=order)

    template = get_template('accounts/invoice.html')
    html = template.render({'order': order, 'order_products': order_products})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


# ---------------------------------------------------
# FORGOT PASSWORD
# ---------------------------------------------------
def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            send_reset_email(request, user)

            messages.success(request, "Password reset email sent 📩")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist ❌")
            return redirect('forgotpassword')

    return render(request, 'accounts/forgotpassword.html')


# ---------------------------------------------------
# RESET PASSWORD VALIDATE
# ---------------------------------------------------
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('resetpassword')
    else:
        messages.error(request, "Link expired ❌")
        return redirect('login')


# ---------------------------------------------------
# RESET PASSWORD
# ---------------------------------------------------
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, "Password reset successful ✅")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match ❌")

    return render(request, 'accounts/resetPassword.html')