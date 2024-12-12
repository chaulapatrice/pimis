from django.core.management.base import BaseCommand, CommandError
from core.utils import submit_batch_job


class Command(BaseCommand):
    help = "Generate sample applications"

    def handle(self, *args, **options):

        try:
            submit_batch_job()
            self.stdout.write(self.style.SUCCESS("🚀 Submitted batch job"))
        except Exception as e:
            raise CommandError(str(e))
