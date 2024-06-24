from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from users.forms import (
    SignUpForm,
    LoginForm,
    SignoutForm
)
from .forms import ApplicationForm, UpdateApplicationForm
from users.models import User
from .models import Application, ApplicantDetails, Payment, Appointment
from django.db import transaction
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from enum import Enum
from .utils import now
from datetime import timedelta


# Create your views here.


def user_signup(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('/')
    error = None
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                cd = form.cleaned_data
                user: User = User.objects.create_user(
                    first_name=cd.get('first_name'),
                    last_name=cd.get('last_name'),
                    username=cd.get('email'),
                    email=cd.get('email'),
                    password=cd.get('password'),
                    phone=cd.get('phone')
                )

                if user is not None:
                    login(request, user)
                    return redirect('/')
                else:
                    error = "Signup failed"

            except Exception as e:
                error = "An error occured"
        else:
            error = 'Enter all required information'
    return render(request, "core/signup.html", {
        'error': error,
        'form': form
    })


def user_signin(request: HttpRequest) -> HttpResponse:
    error = None
    form = LoginForm()

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(
                    username=form.cleaned_data.get('username'),
                    password=form.cleaned_data.get('password')
                )
                if user is not None:
                    login(request, user)
                    next = request.GET.get('next', '/')
                    return redirect(next)
                else:
                    error = 'Invalid login credentials'

            except PermissionDenied as e:
                error = 'Invalid login credentials'
        else:
            error = 'Please enter both password and username'

    return render(request, 'core/login.html', {
        'error': error,
        'form': form
    })


@login_required
def user_logout(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignoutForm(request.POST)
        if form.is_valid():
            logout(request)
            return redirect("signin")
        # You are not supposed to signout any other way :)
        raise PermissionDenied()


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:

    upcoming_appointments = Appointment.objects.filter(
        start__gt=now(),
        application__user=request.user
    )

    peding_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
        application__user=request.user
    )
    return render(request, 'core/dashboard.html', {
        "pending_payments": peding_payments,
        "appointments": upcoming_appointments
    })


class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    paginate_by = 15
    context_object_name = "applications"

    def get_queryset(self) -> QuerySet[Application]:
        return Application.objects.filter(user=self.request.user)


@login_required
def submit_application(request: HttpRequest) -> HttpResponse:
    form = ApplicationForm()
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            with transaction.atomic():
                application = Application.objects.create(
                    type=cd.get('application_type'),
                    is_application_for_someone_else=cd.get(
                        'is_this_application_for_someone_else'),
                    user=request.user
                )

                ApplicantDetails.objects.create(
                    first_name=cd.get('first_name'),
                    last_name=cd.get('last_name'),
                    date_of_birth=cd.get('date_of_birth'),
                    birth_certificate=cd.get('birth_certificate'),
                    national_id=cd.get('national_id', None),
                    street=cd.get('street'),
                    suburb=cd.get('suburb'),
                    city=cd.get('city'),
                    application=application
                )

                try:
                    latest_appointment = Appointment.objects.latest(
                        'created_at')
                    
                    last_end = latest_appointment.end
                    current_time = now()

                    if last_end > current_time:
                        # Check if the time is daylight 
                        if current_time.hour >= 8 and current_time.hour <= 16:
                            start = current_time + timedelta(minutes=5)
                            end = start + timedelta(minutes=20)
                        else:
                            # Add 12 hours to go to daylight 
                            start = current_time + timedelta(minutes=5, hours=12)
                            end = start + timedelta(minutes=20)
                    else:
                        # Check if the time is daylight
                        if current_time.hour >= 8 and current_time.hour <= 16:
                            start = current_time + timedelta(minutes=5, hours=48)
                            end = start + timedelta(minutes=20)
                        else:
                            # Add 12 hours to go to daylight
                            start = current_time + timedelta(minutes=5, days=2, hours=12)
                            end = start + timedelta(minutes=20)


                    Appointment.objects.create(
                        title="Documents Submission",
                        agenda="At the Documents Submission appointment, we will verify and review all required documents "
                        "for accuracy, address any discrepancies, sign necessary forms, and provide a receipt of "
                        "submission. We will also outline any next steps and conclude with a brief Q&A session to "
                        "address any remaining questions or concerns.",
                        start=start,
                        end=end,
                        venue=cd.get('venue'),
                        application=application
                    )
                except Appointment.DoesNotExist:
                    # Check if the time is daylight
                    if current_time.hour >= 8 and current_time.hour <= 16:
                        start = latest_appointment.end + timedelta(minutes=5, days=2)
                        end = start + timedelta(minutes=20)
                    else:
                        # Add 12 hours to go to daylight
                        start = latest_appointment.end + timedelta(minutes=5, days=2, hours=12)
                        end = start + timedelta(minutes=20)

                    Appointment.objects.create(
                        title="Documents Submission",
                        agenda="At the Documents Submission appointment, we will verify and review all required documents "
                        "for accuracy, address any discrepancies, sign necessary forms, and provide a receipt of "
                        "submission. We will also outline any next steps and conclude with a brief Q&A session to "
                        "address any remaining questions or concerns.",
                        start=start,
                        end=end,
                        venue=cd.get('venue'),
                        application=application
                    )

                Payment.objects.create(
                    description='Application Fee',
                    application=application,
                    amount=20
                )
                return redirect(application)

    return render(request, "core/application_form.html", {
        'form': form,
        'title': 'Submit Application'
    })


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    context_object_name = "application"

    def get_queryset(self) -> QuerySet[Application]:
        return Application.objects.filter(user=self.request.user)


@login_required
def update_application(request: HttpRequest, pk=None) -> HttpResponse:
    application = get_object_or_404(Application, pk=pk, user=request.user)
    applicant: ApplicantDetails = application.applicant
    form = UpdateApplicationForm(initial={
        "application_type": application.type,
        "is_this_application_for_someone_else": application.is_application_for_someone_else,
        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "date_of_birth": applicant.date_of_birth,
        "street": applicant.street,
        "suburb": applicant.suburb,
        "city": applicant.city
    })

    if request.method == "POST":
        form = UpdateApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            with transaction.atomic():
                # Update application
                application.type = cd.get('application_type')
                application.is_application_for_someone_else = cd.get(
                    'is_this_application_for_someone_else')
                application.save()

                applicant.first_name = cd.get('first_name')
                applicant.last_name = cd.get('last_name')

                if cd.get('birth_certificate', None):
                    applicant.birth_certificate = cd.get('birth_certificate')

                if cd.get('national_id', None):
                    applicant.national_id = cd.get('national_id')

                applicant.street = cd.get('street')
                applicant.suburb = cd.get('suburb')
                applicant.city = cd.get('city')

                applicant.save()

                return redirect(application)
    return render(request, "core/edit_application_form.html", {
        "form": form,
        "title": f"Edit {application.title()}",
        "application": application
    })


@csrf_exempt
def paynow_webhook(request: HttpRequest, pk=None) -> JsonResponse:
    payment = get_object_or_404(Payment, pk=pk)
    status = request.POST.get('status', None)

    class PaynowPaymentStatus(Enum):
        PAID = "Paid"

    if status == PaynowPaymentStatus.PAID.value:
        payment.status = Payment.Status.COMPLETED
    else:
        payment.status = Payment.Status.FAILED

    payment.save()

    return JsonResponse({
        "message": "Event processed successfully",
        "success": True
    })
