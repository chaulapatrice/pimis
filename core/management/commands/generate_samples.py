from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.utils import now
from users.models import User
from datetime import timedelta
import random
from core.models import (
    Application,
    Appointment,
    ApplicantDetails,
    Payment
)
from faker import Faker


class Command(BaseCommand):
    help = "Generate sample applications"

    def handle(self, *args, **options):
        faker = Faker()
        current_time = now()
        past_time = current_time - timedelta(days=3 * 365)
        past_time = past_time.replace(hour=8, minute=0, second=0, microsecond=0)
        email_counter = 3

        while past_time < current_time:
            count_per_day = random.randint(30, 35)
            count_created_per_day = 0
            while count_created_per_day < count_per_day:
                if past_time > current_time:
                    break
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            first_name=faker.first_name(),
                            last_name=faker.last_name(),
                            username=f"joe{email_counter}@example.com",
                            email=f"joe{email_counter}@example.com",
                            phone=faker.phone_number(),
                        )

                        email_counter += 1
                        application = Application.objects.create(
                            type=random.choice([Application.Type.ID, Application.Type.PASSPORT]),
                            is_application_for_someone_else=random.choice([True, False]),
                            user=user,
                            created_at=past_time - timedelta(days=random.randint(2, 7)),
                            updated_at=past_time + timedelta(days=random.randint(2, 7)),
                            status=Application.Status.APPLICATION_COMPLETED
                        )

                        ApplicantDetails.objects.create(
                            first_name=faker.first_name(),
                            last_name=faker.last_name(),
                            date_of_birth=past_time - timedelta(days=random.randint(365 * 16, 365 * 45)),
                            birth_certificate="/files/2024/12/9/A_story_tell.pdf",
                            national_id="/files/2024/12/9/A_story_tell.pdf",
                            street=faker.name(),
                            suburb=faker.name(),
                            city=faker.name(),
                            application=application
                        )

                        if past_time.hour >= 8 and past_time.hour <= 15:
                            start = past_time
                            end = start + timedelta(minutes=5)
                            past_time = past_time + timedelta(minutes=5)
                        else:
                            start = past_time + timedelta(hours=12)
                            end = start + timedelta(minutes=5)
                            past_time = past_time + timedelta(hours=12)

                        Appointment.objects.create(
                            title="Documents Submission",
                            agenda="At the Documents Submission appointment, we will verify and review all required documents "
                                   "for accuracy, address any discrepancies, sign necessary forms, and provide a receipt of "
                                   "submission. We will also outline any next steps and conclude with a brief Q&A session to "
                                   "address any remaining questions or concerns.",
                            start=start,
                            end=end,
                            venue=random.choice([
                                "Gweru",
                                "Harare",
                                "Bulawayo",
                                "Masvingo",
                                "Mutare",
                                "Chinhoyi",
                                "Mberengwa"
                            ]),
                            application=application
                        )

                        Payment.objects.create(
                            description='Application Fee',
                            application=application,
                            amount=random.randint(100, 120)
                        )

                        print("Application created >>> " + str(application.created_at))

                        count_created_per_day += 1

                except Exception as e:
                    raise CommandError(str(e))
            past_time = past_time.replace(hour=8, minute=0, second=0, microsecond=0)
            past_time = past_time + timedelta(hours=24)

#  User.objects.exclude(username='patrice').delete()
