from django.core.management.base import BaseCommand, CommandError
from users.models import User


class Command(BaseCommand):
    help = "Generate sample applications"

    def handle(self, *args, **options):

        try:
            User.objects.exclude(username='patrice').delete()
        except Exception as e:
            raise CommandError(str(e))
