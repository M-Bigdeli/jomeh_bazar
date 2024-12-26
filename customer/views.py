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
from jomeh_bazar.utils import create_message


def register(request):
    exist_session = all(
        ['verification_code' in request.session, 'first_name' in request.session, 'last_name' in request.session,
         'username' in request.session, 'password' in request.session])
    if request.method == 'POST':
        register_form = CustomerRegisterForm(request.POST)
        if register_form.is_valid():
            phone_number = clean_phone_number(str(register_form.cleaned_data['username']))
            request.session['first_name'] = str(register_form.cleaned_data['first_name'])
            request.session['last_name'] = str(register_form.cleaned_data['last_name'])
            request.session['username'] = phone_number
            request.session['password'] = str(register_form.cleaned_data['password'])
            request.session['verification_code'] = send_verification_code(phone_number)
            return render(request, 'customer/register_code.html', {})
        elif exist_session:
            if 'verification_code' in request.POST and request.session.get('verification_code') == request.POST[
                'verification_code']:
                register_form = CustomerRegisterForm(data={
                    'first_name': request.session.get('first_name', ''),
                    'last_name': request.session.get('last_name', ''),
                    'username': request.session.get('username', ''),
                    'password': request.session.get('password', ''),
                })
                if register_form.is_valid():
                    request.session.flush()
                    user = register_form.save(commit=False)
                    user.password = make_password(register_form.cleaned_data['password'])
                    user.save()
                    login(request, user)
                    create_message(request, "خوش آمدید!", 3, "bxs-smile")
                    return redirect(reverse('home:home'))
                else:
                    request.session.flush()
                    register_form = CustomerRegisterForm()
            else:
                create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
                return render(request, 'customer/register_code.html', {})
        else:
            register_form = CustomerRegisterForm()
    else:
        if exist_session:
            return render(request, 'customer/register_code.html', {})
        else:
            register_form = CustomerRegisterForm()

    return render(request, 'customer/register.html', {'form': register_form})


def reset_session(request, rote):
    request.session.flush()
    return redirect(reverse(rote))


def log_in(request):
    if request.method == 'POST':
        log_in_form = CustomerLogInForm(request.POST)
        if log_in_form.is_valid():
            username = clean_phone_number(str(log_in_form.cleaned_data['username']))
            password = log_in_form.cleaned_data['password']

            try:
                user = Customer.objects.get(username=username)
                if user.check_password(password):
                    login(request, user)
                    create_message(request, "خوش آمدید!", 3, "bxs-smile")
                    return redirect(reverse('home:home'))
                else:
                    create_message(request, "رمز عبور اشتباه است!", 1, "bx-x")
                    return render(request, 'customer/log_in.html', {'form': log_in_form})
            except Customer.DoesNotExist:
                create_message(request, "این کاربر وجود ندارد!", 2, "bxs-user-x")
                return render(request, 'customer/log_in.html', {'form': log_in_form})
        else:
            log_in_form = CustomerLogInForm()
    else:
        log_in_form = CustomerLogInForm()

    return render(request, 'customer/log_in.html', {'form': log_in_form})


def forget_password(request):
    exist_session = all(['verification_code' in request.session, 'username' in request.session])
    if request.method == 'POST':
        if exist_session:
            if request.session.get('verification_code') == request.POST['verification_code']:
                change_password_form = ChangePasswordForm(request.POST)
                if change_password_form.is_valid():
                    user = Customer.objects.get(username=request.session['username'])
                    request.session.flush()
                    user.set_password(str(change_password_form.cleaned_data['password']))
                    user.save()
                    create_message(request, "رمز عبور شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
                    return redirect(reverse('customer:log_in'))
                else:
                    request.session.flush()
                    forget_password_form = ForgetPasswordForm()
            else:
                change_password_form = ChangePasswordForm()
                create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
                return render(request, 'customer/change_password.html', {'form': change_password_form})
        else:
            forget_password_form = ForgetPasswordForm(request.POST)
            if forget_password_form.is_valid():
                username = clean_phone_number(str(forget_password_form.cleaned_data['username']))

                try:
                    Customer.objects.get(username=username)
                    request.session['username'] = str(username)
                    request.session['verification_code'] = send_verification_code(username)
                    change_password_form = ChangePasswordForm()
                    return render(request, 'customer/change_password.html', {'form': change_password_form})

                except Customer.DoesNotExist:
                    create_message(request, "این کاربر وجود ندارد!", 2, "bxs-user-x")
                    return render(request, 'customer/forget_password.html', {'form': forget_password_form})
            else:
                forget_password_form = ForgetPasswordForm()
    else:
        if exist_session:
            change_password_form = ChangePasswordForm()
            return render(request, 'customer/change_password.html', {'form': change_password_form})
        else:
            forget_password_form = ForgetPasswordForm()
    return render(request, 'customer/forget_password.html', {'form': forget_password_form})


def change_forgotten_password(request):
    exist_session = all(['verification_code' in request.session, 'username' in request.session])
    if request.method == 'POST' and exist_session:
        if request.session.get('verification_code') == request.POST['verification_code']:
            change_password_form = ChangePasswordForm(request.POST)
            if change_password_form.is_valid():
                user = Customer.objects.get(username=request.session['username'])
                request.session.flush()
                user.set_password(str(change_password_form.cleaned_data['password']))
                user.save()
                create_message(request, "رمز عبور شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
                return redirect(reverse('customer:log_in'))
            else:
                request.session.flush()
                return redirect(reverse('customer:register'))
        else:
            change_password_form = ChangePasswordForm()
            create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
            return render(request, 'customer/change_password.html', {'form': change_password_form})
    else:
        if exist_session:
            change_password_form = ChangePasswordForm()
            return render(request, 'customer/change_password.html', {'form': change_password_form})
        else:
            request.session.flush()
            return redirect(reverse('customer:register'))


@login_required(login_url='customer:log_in')
def log_out(request):
    logout(request)
    create_message(request, "از حساب کاربری خود خارج شدید!", 2, "bxs-check-circle")
    return redirect(reverse('home:home'))


@login_required(login_url='customer:log_in')
def account(request):
    request.session.delete('verification_code')
    request.session.delete('username')
    context = {'change_password_form': ChangePasswordAuthenticatedUserForm(),
               'change_name_form': ChangeNameForm(instance=request.user),
               'address_form': AddressForm(),
               'addresses': [[AddressForm(instance=address), address.id] for address in
                             Address.objects.filter(customer=request.user)], }

    return render(request, 'customer/account.html', context)


def change_name(request):
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
            username = clean_phone_number(request.POST.get('username'))
            if not Customer.objects.filter(username=username).exists():
                request.session['verification_code'] = send_verification_code(request.POST.get('username'))
                request.session['username'] = username
                return render(request, 'customer/change_phone_number.html', {})
            else:
                create_message(request, "این شماره تلفن قبلا ثبت شده!", 2, "bxs-error-circle")
                return redirect(reverse('customer:account'))
        elif 'verification_code' in request.POST:
            if request.POST.get('verification_code') == request.session.get('verification_code'):
                user = Customer.objects.get(username=request.user.username)
                user.username = request.session.get('username')
                user.save()
                request.session.delete('verification_code')
                request.session.delete('username')
                create_message(request, "شماره تلفن شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
                return redirect(reverse('customer:account'))
            else:
                create_message(request, "کد وارد شده اشتباه است!", 1, "bxs-comment-x")
                return render(request, 'customer/change_phone_number.html', {})

    return render(request, 'customer/change_phone_number.html', {})


@login_required(login_url='customer:log_in')
def change_password(request):
    if request.method == 'POST':
        change_password_form = ChangePasswordAuthenticatedUserForm(request.POST)
        if change_password_form.is_valid():
            if request.user.check_password(change_password_form.cleaned_data['password']):
                request.user.set_password(change_password_form.cleaned_data['new_password'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                create_message(request, "رمز عبور شما با موفقیت تغییر یافت!", 3, "bxs-check-circle")
            else:
                create_message(request, "رمز عبور اشتباه است!", 1, "bx-x")

    return redirect(reverse('customer:account'))


@login_required(login_url='customer:log_in')
def add_address(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.customer = request.user
            address.save()
            create_message(request, "آدرس شما با موفقیت اضافه شد!", 3, "bxs-check-circle")

    return redirect(reverse('customer:account'))


@login_required(login_url='customer:log_in')
def edit_address(request):
    if request.method == 'POST' and 'edit_address' in request.POST:
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            try:
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
    if request.method == 'POST' and 'delete_address' in request.POST:
        try:
            address = Address.objects.get(id=request.POST.get('delete_address'), customer=request.user)
            address.delete()
            create_message(request, "آدرس شما حذف شد!", 2, "bxs-check-circle")
        except Address.DoesNotExist:
            pass

    return redirect(reverse('customer:account'))
