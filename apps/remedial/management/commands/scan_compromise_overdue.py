from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.remedial import models, services


class Command(BaseCommand):
    help = "Mark overdue compromise schedule items and trigger defaults."
    lock_id = 280419

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [self.lock_id])
            locked = cursor.fetchone()[0]
            if not locked:
                self.stdout.write(self.style.WARNING("Skipping scan: lock already held."))
                return
            try:
                self.stdout.write("Scanning compromise schedule items for overdue/default.")
                items = models.CompromiseScheduleItem.objects.select_related("compromise_agreement").filter(
                    status__in=[models.ScheduleStatus.DUE, models.ScheduleStatus.PARTIAL]
                )
                for item in items:
                    services.detect_schedule_default(item)
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [self.lock_id])
