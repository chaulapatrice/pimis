from django.contrib import admin
from django.http import HttpResponse
from django.db.models import QuerySet
from .models import (
    ApplicantDetails,
    Application,
    Payment,
    Appointment
)
from openpyxl import Workbook
# Register your models here.


class ApplicantDetailsInline(admin.StackedInline):
    model = ApplicantDetails


class PaymentInline(admin.TabularInline):
    model = Payment


class AppointmentInline(admin.TabularInline):
    model = Appointment

@admin.action(description='Geneate Excel Report')
def generate_excel_report(modeladmin, request, queryset: QuerySet[Application]):
    workbook = Workbook()
    headers = [
        'Applicant Name',
        'Application Status',
        'Application Type',
        'Total Revenue'
    ]
    worksheet =workbook.active
    worksheet.append(headers)

    for application in queryset:
        payments = Payment.objects.filter(application=application)
        total_payments = sum([float(payment.amount) for payment in payments])
        row = [
            f"{application.applicant.first_name} {application.applicant.last_name}",
            application.status,
            application.type,
            total_payments
        ]

        worksheet.append(row)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="selected_items.xlsx"'

        workbook.save(response)
        return response

@admin.register(Application)
class ApplicationModelAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "type",
        "status"
    ]

    inlines = [
        ApplicantDetailsInline,
        PaymentInline,
        AppointmentInline
    ]

    actions = [generate_excel_report]


@admin.register(Appointment)
class AppointmentModelAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'agenda',
        'start',
        'end'
    ]
