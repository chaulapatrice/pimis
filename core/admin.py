from django.contrib import admin
from django.db.models import QuerySet
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


@admin.action(description='Geneate Excel Report')
def generate_report(modeladmin, request, queryset: QuerySet[Application]):
    pass


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

    actions = [generate_report]


@admin.register(Appointment)
class AppointmentModelAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'agenda',
        'start',
        'end'
    ]
