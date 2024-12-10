from django.core.management.base import BaseCommand, CommandError
from core.models import generate_excel_report


class Command(BaseCommand):
    help = "Generate sample applications"

    def handle(self, *args, **options):

        try:
            generate_excel_report()
        except Exception as e:
            raise CommandError(str(e))

