from django.contrib import admin
from .models import (
    ApplicantDetails,
    Application,
    Payment,
    Appointment
)
# Register your models here.


class ApplicantDetailsInline(admin.StackedInline):
    model = ApplicantDetails


class PaymentInline(admin.TabularInline):
    model = Payment


class AppointmentInline(admin.TabularInline):
    model = Appointment


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


@admin.register(Appointment)
class AppointmentModelAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'agenda',
        'start',
        'end'
    ]
