from django.shortcuts import render, redirect
from .models import User, Service, Payment, InformReport
from .forms import RegisterForm, LoginForm, AccountEditForm
from common.decorators import ajax_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from rest_framework import permissions, viewsets, generics
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .serializers import UserSerializer, ServiceSerializer, InformSerializer
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, FileResponse
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
import datetime
import requests
import random
import json


from ippanel import Client
from ippanel import HTTPError

SMS_APIKEY = 'wXW-56fPIx4uBBC_VtTgJsZT2jAIGA_dS0pmY_jn4rw='
SMS_PATTERN_CODE = '46jgf54byb5c60t'
SMS_SENDER = "+983000505"
sms = Client(SMS_APIKEY)


if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

CallbackURL = 'https://khcbus.ir/pay/verify'

AMOUNT = 30_000
description = "حساب پریمیوم ماهانه"
email = 'email@example.com'
mobile = '09123456789'


def sub_check(u):
    def check(request, *args, **kwargs):
        if not request.user.sub_expire_date > timezone.now():
            return redirect('/subscription')
        return u(request, *args, **kwargs)

    return check


def home(request):

    return render(request, "index.html")


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            form = RegisterForm()

            return render(request, "auth.html",
                          {"form": form, "status": "green", "login": "Y",
                           "message": "ثبت نام شما با موفقیت انجام شد، وارد شوید."})
        else:
            return render(request, "auth.html",
                          {"form": form, "status": "red",
                           "message": "ثبت نام شما با خطا مواجه شد، دوباره تلاش کنید."})

    form = RegisterForm()
    return render(request, "auth.html",
                  {"form": form})


@ajax_required
@require_POST
def get_otp(request):
    number = request.POST.get('number')
    if number:
        otp_code = random.randint(1000, 9999)
        message_id = sms.send_pattern(
            SMS_PATTERN_CODE,
            SMS_SENDER,
            f"+98{number}",
            {"code": f"{otp_code}"},
        )

        return JsonResponse({'status': 'ok', 'otp': otp_code}, status=200)
    else:
        return JsonResponse({'status': 'error'}, status=400)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                phone_number=cd['phone_number'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('account:dashboard')
                else:
                    return render(request, "login.html",
                                  {"form": form, "status": "red", "message": "حساب شما غیرفعال است."})
            else:
                return render(request, "login.html",
                              {"form": form, "status": "red", "message": "شماره همراه یا رمز عبور نامعتبر است."})

    form = LoginForm()
    return render(request, "login.html",
                  {"form": form})


@login_required
def dashboard(request):

    return render(request, "dashboard.html",
                  {"title": "داشبورد"})


@login_required
def account(request):
    if request.method == 'POST':
        form = AccountEditForm(data=request.POST, instance=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.save(commit=False)
            if cd['password2'] != "" and user.check_password(cd['password']):
                user.set_password(cd['password2'])
            user.save()

            return render(request, "account.html",
                          {"title": "حساب کاربری",
                           "user": request.user, "form": form, "status": "green",
                           "message": "ویرایش اطلاعات حساب شما با موفقیت انجام شد."})
        else:
            return render(request, "account.html",
                          {"title": "حساب کاربری",
                           "user": request.user, "form": form, "status": "red",
                           "message": "ویرایش اطلاعات حساب شما با خطا مواجه شد."})

    form = AccountEditForm(instance=request.user)
    return render(request, "account.html",
                  {"title": "حساب کاربری",
                   "user": request.user,
                   "form": form})


@login_required
def subscription(request):

    return render(request, "subscription.html",
                  {"title": "اشتراک پریمیوم"})


def send_request(request):
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": AMOUNT,
        "Description": description,
        "Phone": request.user.phone_number,
        "CallbackURL": CallbackURL,
    }
    data = json.dumps(data)
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    try:
        response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                # return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                #        'authority': response['Authority']}
                return redirect(ZP_API_STARTPAY + str(response['Authority']))
            else:
                # return {'status': False, 'code': str(response['Status'])}
                return HttpResponse(f'Error code: {str(response["Status"])}')
        # return response
        return HttpResponse(f'Error code: {str(response)}')

    except requests.exceptions.Timeout:
        # return {'status': False, 'code': 'timeout'}
        return HttpResponse(f'Error code: timeout')
    except requests.exceptions.ConnectionError:
        # return {'status': False, 'code': 'connection error'}
        return HttpResponse(f'Error code: connection error')


def pay_verify(request):
    authority = request.GET['Authority']
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": AMOUNT,
        "Authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            # return {'status': True, 'RefID': response['RefID']}
            user = request.user
            if user.sub_expire_date > timezone.now():
                user.sub_expire_date += datetime.timedelta(days=30)
            else:
                user.sub_expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
            user.save()

            Payment.objects.create(user=user,
                                   description="موفق | تمدید ماهانه اشتراک",
                                   price=AMOUNT,
                                   status="موفق")

            return render(request, 'subscription.html',
                          {'title': 'پرداخت اشتراک پریمیوم',
                           'message': 'عملیات پرداخت موفق بوده و اشتراک حساب شما تمدید شد.',
                           'color': 'green'})
        else:
            # return {'status': False, 'code': str(response['Status'])}
            Payment.objects.create(user=request.user,
                                   description="تمدید ماهانه اشتراک",
                                   price=AMOUNT,
                                   status="ناموفق")
            return render(request, 'subscription.html',
                          {'title': 'پرداخت اشتراک پریمیوم',
                           'message': 'پرداخت ناموفق بود. در صورت کسر وجه از حساب تا 48 ساعت آینده عودت خواهد شد.',
                           'color': 'red'})
    # return response
    return render(request, 'subscription.html',
                  {'title': 'پرداخت حساب پریمیوم',
                   'message': 'عملیات پرداخت با خطا مواجه شد. دوباره مراحل را تکرار کنید.',
                   'color': 'red'})


@sub_check
@login_required
def set_reminder(request):
    if request.method == 'POST':
        s_ids = request.POST.getlist('services[]')
        if s_ids:
            for serv in s_ids:
                service = Service.objects.get(id=serv)
                service.passengers.add(request.user)

            return JsonResponse({'status': 'ok'}, status=200)
        else:
            return JsonResponse({'status': 'error'}, status=400)

    services = Service.objects.filter(expired=False)
    services_new = []
    for serv in services:
        if request.user not in serv.passengers.all():
            services_new.append(serv)
    destinations = ["اصفهان به خوانسار", "خوانسار به اصفهان"]

    return render(request, "set-reminders.html",
                  {"title": "ثبت انتظار بلیط",
                   "services": services_new, "destinations": destinations})


@login_required
def waiting_list(request):
    if request.method == 'POST':
        s_id = request.POST.get('id')
        if s_id:
            service = Service.objects.get(id=s_id)
            service.passengers.remove(request.user)

            return JsonResponse({'status': 'ok'}, status=200)
        else:
            return JsonResponse({'status': 'error'}, status=400)

    services = request.user.service_passengers.filter(expired=False)

    return render(request, "waiting-list.html",
                  {"title": "لیست انتظار شما",
                   "services": services})


@login_required
def inform_report(request):
    informs = request.user.user_sms_report.all()

    return render(request, "inform-report.html",
                  {"title": "پیام های ارسال شده",
                   "informs": informs})


@login_required
def payments_report(request):
    pays = request.user.user_payments.all()

    return render(request, "payments-report.html",
                  {"title": "پرداخت ها",
                   "pays": pays})


class ServiceViewSet(viewsets.ModelViewSet):

    queryset = Service.objects.filter(expired=False).order_by('datetime')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]


class InformListCreateView(viewsets.ModelViewSet):

    queryset = InformReport.objects.all().order_by('datetime')
    serializer_class = InformSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
