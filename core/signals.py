from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction
from .models import PredictionJob, Payment
from django.conf import settings
from django.db import transaction
from paynow import Paynow
from django.contrib.sites.models import Site
from django.urls import reverse
from core.tasks import run_prediction_job


@receiver(post_save, sender=PredictionJob)
def post_save_predication_job(sender, instance: PredictionJob, created, **kwargs):
    if created:
        run_prediction_job.delay(instance.pk)

# @receiver(post_save, sender=Payment)
# def post_save_payment(sender, instance: Payment, created, **kwargs):
#     if instance.paynow_poll_url == None:
#         with transaction.atomic():
#             current_site = Site.objects.get(pk=getattr(settings, 'SITE_ID'))
#
#             return_url = "http://localhost:8000" + reverse('application_detail', kwargs={
#                 "pk": instance.application.pk
#             })
#
#             result_url = current_site.domain + reverse('paynow_webhook', kwargs={
#                 "pk": instance.pk
#             })
#
#             paynow = Paynow(
#                 getattr(settings, 'PAYNOW_INTEGRATION_ID'),
#                 getattr(settings, 'PAYNOW_INTEGRATION_KEY'),
#                 return_url,
#                 result_url
#             )
#
#             payment = paynow.create_payment(
#                 instance.application.title(),
#                 'chaulapatrice@gmail.com'
#             )
#
#             payment.add(
#                 instance.application.title(),
#                 float(instance.amount)
#             )
#
#             response = paynow.send(payment)
#
#             if response.success:
#                 instance.paynow_poll_url = response.poll_url
#                 instance.paynow_redirect_url = response.redirect_url
#                 instance.save()
