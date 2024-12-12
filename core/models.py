import pytz
from django.db import models
from .utils import now
from urllib.parse import quote
from django.urls import reverse
from openpyxl import Workbook
from datetime import datetime
import boto3
import os


# Create your models here.


class Application(models.Model):
    class Type(models.TextChoices):
        PASSPORT = "Passport", "Passport"
        ID = "ID", "ID"

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPLICATION_RECEIVED = "Application Received", "Application Received"
        APPLICATION_REJECTED = "Application Rejected", "Application Rejected"
        APPOINTMENT_SCHEDULED = "Appointment Scheduled", "Appointment Scheduled"
        PROCESSING = "Processing", "Processing"
        READY_FOR_COLLECTION = "Ready For Collection", "Ready For Collection"
        APPLICATION_COMPLETED = "Application Completed", "Application Completed"

    status = models.CharField(
        max_length=45, choices=Status, default=Status.PENDING)
    is_application_for_someone_else = models.BooleanField(default=False)
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='applications')
    type = models.CharField(max_length=45, choices=Type)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def title(self) -> str:
        return f"{self.type} application - {self.applicant.first_name} {self.applicant.last_name}"

    def __str__(self) -> str:
        return self.title()

    def status_class(self) -> str:
        if self.status == Application.Status.PENDING:
            return 'bg-secondary'
        if self.status == Application.Status.APPLICATION_RECEIVED:
            return 'bg-info'
        if self.status == Application.Status.APPLICATION_REJECTED:
            return 'bg-danger'
        if self.status == Application.Status.APPOINTMENT_SCHEDULED:
            return 'bg-info'
        if self.status == Application.Status.PROCESSING:
            return 'bg-info'
        if self.status == Application.Status.READY_FOR_COLLECTION:
            return 'bg-success'
        if self.status == Application.Status.APPLICATION_COMPLETED:
            return 'bg-success'

    def get_absolute_url(self) -> str:
        return reverse("application_detail", kwargs={'pk': self.pk})


class ApplicantDetails(models.Model):
    current_date = now()
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    date_of_birth = models.DateField()
    birth_certificate = models.FileField(
        upload_to=f"files/{current_date.year}/{current_date.month}/{current_date.day}")
    national_id = models.FileField(
        upload_to=f"files/{current_date.year}/{current_date.month}/{current_date.day}")
    street = models.CharField(max_length=150)
    suburb = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="applicant")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.first_name + self.last_name


class Appointment(models.Model):
    title = models.CharField(max_length=255)
    agenda = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Venue(models.TextChoices):
        HARARE = 'Harare', 'Harare'
        GWERU = 'Gweru', 'Gweru'
        MBERENGWA = 'Mberengwa', 'Mberengwa'
        BULAWAYO = 'Bulawayo', 'Bulawayo'
        MASVINGO = 'Masvingo', 'Masvingo'

    venue = models.CharField(max_length=255, choices=Venue)
    application = models.ForeignKey(
        "Application", on_delete=models.CASCADE, related_name="appointments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Appointment for {self.application.title}"

    def add_to_calendar_url(self):
        base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
        title = quote(self.title)
        details = quote(self.agenda)
        start_datetime = self.start.strftime(
            "%Y%m%dT%H%M%S")
        end_datetime = self.end.strftime("%Y%m%dT%H%M%S")
        location = quote(self.venue)

        return f"{base_url}&text={title}&dates={start_datetime}/{end_datetime}&location={location}&sf=true&output=xml&details={details}"


class Payment(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"

    status = models.CharField(choices=Status, default=Status.PENDING)
    application = models.ForeignKey(
        "Application", on_delete=models.CASCADE, related_name="payments")
    paynow_redirect_url = models.CharField(
        max_length=255, null=True, blank=True)
    paynow_poll_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def status_class(self) -> str:
        if self.status == Payment.Status.PENDING:
            return 'bg-secondary'
        if self.status == Payment.Status.FAILED:
            return 'bg-danger'
        if self.status == Payment.Status.COMPLETED:
            return 'bg-success'

    def __str__(self) -> str:
        return f"Payment for {self.application.title()}"


def generate_excel_report(show_logs=False):
    queryset = Application.objects.filter(
        created_at__lte=datetime(2024, 11, 30, hour=23, minute=59, second=59)
    ).exclude()
    workbook = Workbook()
    headers = [
        'Date Created',
        'Applicant Name',
        'Application Status',
        'Application Type',
        'Total Revenue'
    ]
    worksheet = workbook.active
    worksheet.append(headers)
    processed_application_number = 1
    total_application_count = queryset.count()
    for application in queryset:
        payments = Payment.objects.filter(application=application)
        total_payments = sum([float(payment.amount) for payment in payments])
        row = [
            application.created_at.strftime("%Y-%m-%d"),
            f"{application.applicant.first_name} {application.applicant.last_name}",
            application.status,
            application.type,
            total_payments
        ]

        worksheet.append(row)
        print("Processed Application >> ", f"{processed_application_number}/{total_application_count}")
        processed_application_number += 1

    workbook.save("/media/exports.xlsx")


class PredictionJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        RUNNING = "Running", "Running"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"

    status = models.CharField(choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    graph = models.FileField(upload_to="results/", null=True, blank=True)
    actual = models.FileField(upload_to="results/", null=True, blank=True)
    forecast = models.FileField(upload_to="results/", null=True, blank=True)
    actual_prediction = models.FileField(upload_to="results/", null=True, blank=True)
