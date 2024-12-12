from django.core.management.base import BaseCommand, CommandError
from core.models import generate_excel_report


class Command(BaseCommand):
    help = "Generate excel report"

    def handle(self, *args, **options):

        try:
            self.stdout.write("Generating report...")
            generate_excel_report()
            self.stdout.write(self.style.SUCCESS("🚀 Successfully generated report."))
        except Exception as e:
            raise CommandError(str(e))
