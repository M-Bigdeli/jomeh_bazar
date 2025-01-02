from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from .models import Customer, Address
from .forms import CustomerRegisterForm, CustomerLogInForm, ForgetPasswordForm, ChangePasswordForm, \
    ChangePasswordAuthenticatedUserForm, ChangeNameForm, AddressForm
from .utils import clean_phone_number, send_verification_code
from customer.decorators import redirect_if_authenticated
from message.utils import create_message


# User authentication views:

@redirect_if_authenticated(redirect_url='customer:account')
def register(request):
    """
    This view register the user as customer.
    """
    # Checking for the existence of sessions related to user registration.
    exist_session = all(
        ['verification_code' in request.session, 'first_name' in request.session, 'last_name' in request.session,
         'username' in request.session, 'password' in request.session])
    if request.method == 'POST':
        register_form = CustomerRegisterForm(request.POST)
        if register_form.is_valid():
            # User submit register form. Save form data as session and send code to user`s phone number.
            phone_number = clean_phone_number(str(register_form.cleaned_data['username']))
            request.session['first_name'] = str(register_form.cleaned_data['first_name'])
            request.session['last_name'] = str(register_form.cleaned_data['last_name'])
            request.session['username'] = phone_number
            request.session['password'] = str(register_form.cleaned_data['password'])
            request.session['verification_code'] = send_verification_code(phone_number)
            # Redirect the user to the code entry page.
            return render(request, 'customer/register_code.html', {})
        elif exist_session:
            # User submit the code.
            if 'verification_code' in request.POST and request.session.get('verification_code') == request.POST[
                'verification_code']:
                # Code is correct. register the customer.
                user = Customer()
                user.first_name = request.session.get('first_name')
                user.last_name = request.session.get('last_name')
                user.username = request.session.get('username')
                # hash password whit Django hash algorithm.
                user.password = make_password(request.session.get('password'))
                request.session.flush()
                user.save()
                login(request, user)
                create_message(request, "خوش آمدید!", 3, "bxs-smile")
                return redirect(reverse('home:home'))
            else:
                # Code is wrong.
                create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
                return render(request, 'customer/register_code.html', {})
        else:
            # An unusual request has been sent.
            register_form = CustomerRegisterForm()
    else:
        if exist_session:
            # Register code page refreshed.
            return render(request, 'customer/register_code.html', {})
        else:
            # User now enters register page.
            register_form = CustomerRegisterForm()

    return render(request, 'customer/register.html', {'form': register_form})


def reset_session(request, rote='home:home'):
    """
    This view reset all sessions and redirect to url.
    :param request:
    :param rote: Destination URL in this Django project.
    """
    request.session.flush()
    return redirect(reverse(rote))


@redirect_if_authenticated(redirect_url='customer:account')
def log_in(request):
    """
        This view authentication the user as customer.
    """
    if request.method == 'POST':
        # User submit login form.
        log_in_form = CustomerLogInForm(request.POST)
        if log_in_form.is_valid():
            username = clean_phone_number(str(log_in_form.cleaned_data['username']))
            password = log_in_form.cleaned_data['password']

            try:
                # User authentication and account login.
                user = Customer.objects.get(username=username)
                if user.check_password(password):
                    # The password is correct.
                    login(request, user)
                    create_message(request, "خوش آمدید!", 3, "bxs-smile")
                    return redirect(reverse('home:home'))
                else:
                    # The password is wrong.
                    create_message(request, "رمز عبور اشتباه است!", 1, "bx-x")
                    return render(request, 'customer/log_in.html', {'form': log_in_form})
            except Customer.DoesNotExist:
                # User does not exist.
                create_message(request, "این کاربر وجود ندارد!", 2, "bxs-user-x")
                return render(request, 'customer/log_in.html', {'form': log_in_form})
        else:
            # An unusual request has been sent.
            log_in_form = CustomerLogInForm()
    else:
        # User now enters login page.
        log_in_form = CustomerLogInForm()

    return render(request, 'customer/log_in.html', {'form': log_in_form})


@redirect_if_authenticated(redirect_url='customer:account')
def forget_password(request):
    """
        This view changes the password of a user who has forgotten their password by sending a code to the customer's phone number.
    """
    exist_session = all(['verification_code' in request.session, 'username' in request.session])
    if request.method == 'POST':
        if exist_session:
            # User submit change password form.
            if request.session.get('verification_code') == request.POST['verification_code']:
                # The user entered the sent code correctly.
                change_password_form = ChangePasswordForm(request.POST)
                if change_password_form.is_valid():
                    # Change password of user.
                    user = Customer.objects.get(username=request.session['username'])
                    request.session.flush()
                    user.set_password(str(change_password_form.cleaned_data['password']))
                    user.save()
                    create_message(request, "رمز عبور شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
                    return redirect(reverse('customer:log_in'))
                else:
                    # An unusual request has been sent.
                    request.session.flush()
                    forget_password_form = ForgetPasswordForm()
            else:
                # The user entered the sent code incorrectly.
                change_password_form = ChangePasswordForm()
                create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
                return render(request, 'customer/change_password.html', {'form': change_password_form})
        else:
            # User submit login form.
            forget_password_form = ForgetPasswordForm(request.POST)
            if forget_password_form.is_valid():
                username = clean_phone_number(str(forget_password_form.cleaned_data['username']))

                try:
                    # The username and code sent are saved as a session. The user is redirected to the password change page.
                    Customer.objects.get(username=username)
                    request.session['username'] = str(username)
                    request.session['verification_code'] = send_verification_code(username)
                    change_password_form = ChangePasswordForm()
                    return render(request, 'customer/change_password.html', {'form': change_password_form})

                except Customer.DoesNotExist:
                    # User does not exist.
                    create_message(request, "این کاربر وجود ندارد!", 2, "bxs-user-x")
                    return render(request, 'customer/forget_password.html', {'form': forget_password_form})
            else:
                # An unusual request has been sent.
                forget_password_form = ForgetPasswordForm()
    else:
        if exist_session:
            # User now enters change password page.
            change_password_form = ChangePasswordForm()
            return render(request, 'customer/change_password.html', {'form': change_password_form})
        else:
            # User now enters forget password page.
            forget_password_form = ForgetPasswordForm()

    return render(request, 'customer/forget_password.html', {'form': forget_password_form})

# End user authentication views.


# Account settings views:

@login_required(login_url='customer:log_in')
def log_out(request):
    """
        This view logout the user.
    """
    logout(request)
    create_message(request, "از حساب کاربری خود خارج شدید!", 2, "bxs-check-circle")
    return redirect(reverse('home:home'))


@login_required(login_url='customer:log_in')
def account(request):
    """
        This view shows the user the account settings section along with its related forms.
    """
    request.session.delete('verification_code')
    request.session.delete('username')
    context = {'change_password_form': ChangePasswordAuthenticatedUserForm(),
               'change_name_form': ChangeNameForm(instance=request.user),
               'address_form': AddressForm(),
               # Display addresses registered by the user.
               'addresses': [[AddressForm(instance=address), address.id] for address in
                             Address.objects.filter(customer=request.user)], }

    return render(request, 'customer/account.html', context)


@login_required(login_url='customer:log_in')
def change_name(request):
    """
        This view changes the first name amd last name of a user.
    """
    if request.method == 'POST':
        change_name_form = ChangeNameForm(request.POST, instance=request.user)
        if change_name_form.is_valid():
            change_name_form.save()
            create_message(request, "نام شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")

    return redirect(reverse('customer:account'))


@login_required(login_url='customer:log_in')
def change_phone_number(request):
    if request.method == 'POST':
        if 'username' in request.POST:
            # User submit change phone number form.
            username = clean_phone_number(request.POST.get('username'))
            if not Customer.objects.filter(username=username).exists():
                # The phone number is not previously registered and is new.
                request.session['verification_code'] = send_verification_code(request.POST.get('username'))
                request.session['username'] = username
                return render(request, 'customer/change_phone_number.html', {})
            else:
                # The phone number is already registered and is a duplicate. It may belong to another user.
                create_message(request, "این شماره تلفن قبلا ثبت شده!", 2, "bxs-error-circle")
                return redirect(reverse('customer:account'))
        elif 'verification_code' in request.POST:
            # User submit code entered form.
            if request.POST.get('verification_code') == request.session.get('verification_code'):
                # The user enters the code correctly and their phone number changes.
                user = Customer.objects.get(username=request.user.username)
                user.username = request.session.get('username')
                user.save()
                request.session.delete('verification_code')
                request.session.delete('username')
                create_message(request, "شماره تلفن شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
                return redirect(reverse('customer:account'))
            else:
                # Code is wrong.
                create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
                return render(request, 'customer/change_phone_number.html', {})

    return render(request, 'customer/change_phone_number.html', {})


@login_required(login_url='customer:log_in')
def change_password(request):
    """
        This view changes the password of a user. For this user, the old password of the user must be entered correctly.
    """
    if request.method == 'POST':
        change_password_form = ChangePasswordAuthenticatedUserForm(request.POST)
        if change_password_form.is_valid():
            if request.user.check_password(change_password_form.cleaned_data['password']):
                # The user entered their old password correctly.
                request.user.set_password(change_password_form.cleaned_data['new_password'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                create_message(request, "رمز عبور شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
            else:
                # The user entered their old password incorrectly.
                create_message(request, "رمز عبور اشتباه است!", 1, "bx-x")

    return redirect(reverse('customer:account'))


@login_required(login_url='customer:log_in')
def add_address(request):
    """
    This view add a new address for a User.
    """
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            # add address.
            address = address_form.save(commit=False)
            address.customer = request.user
            address.save()
            create_message(request, "آدرس شما با موفقیت اضافه شد!", 3, "bxs-check-circle")

    return redirect(reverse('customer:account'))


@login_required(login_url='customer:log_in')
def edit_address(request):
    """
    This view edit a user's address.
    """
    if request.method == 'POST' and 'edit_address' in request.POST:
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            try:
                # Edit address of User.
                # Obtaining the address associated with the authenticated user.
                address = Address.objects.get(id=request.POST.get('edit_address'), customer=request.user)
                address.state = address_form.cleaned_data['state']
                address.city = address_form.cleaned_data['city']
                address.address = address_form.cleaned_data['address']
                address.postal_code = address_form.cleaned_data['postal_code']
                address.save()
                create_message(request, "آدرس شما با موفقیت ویرایش شد!", 3, "bxs-check-circle")
            except Address.DoesNotExist:
                pass

    return redirect(reverse('customer:account'))


@login_required(login_url='customer:log_in')
def delete_address(request):
    """
    This view deletes a user's address.
    """
    if request.method == 'POST' and 'delete_address' in request.POST:
        try:
            # Delete address of User.
            # Obtaining the address associated with the authenticated user.
            address = Address.objects.get(id=request.POST.get('delete_address'), customer=request.user)
            address.delete()
            create_message(request, "آدرس شما حذف شد!", 2, "bxs-check-circle")
        except Address.DoesNotExist:
            pass

    return redirect(reverse('customer:account'))

# ٍEnd account settings views.
