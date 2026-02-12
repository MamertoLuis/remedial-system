from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.remedial import models, services


class Command(BaseCommand):
    help = "Scan for overdue recovery milestones and trigger escalations."
    lock_id = 280422

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [self.lock_id])
            locked = cursor.fetchone()[0]
            if not locked:
                self.stdout.write(self.style.WARNING("Skipping milestone scan: lock already held."))
                return
            try:
                self.stdout.write("Scanning recovery milestones for overdue items...")
                
                # Find overdue milestones (past target_date)
                overdue_milestones = models.RecoveryMilestone.objects.filter(
                    target_date__lt=timezone.now().date(),
                    status="pending"
                ).select_related("recovery_action")
                
                escalated_count = 0
                for milestone in overdue_milestones:
                    milestone.status = "overdue"
                    milestone.escalation_sent_at = timezone.now()
                    milestone.save(update_fields=["status", "escalation_sent_at"])
                    
                    escalated_count += 1
                    
                    # Log the escalation
                    self.stdout.write(
                        f"Escalated milestone {milestone.pk} for "
                        f"account {milestone.recovery_action.remedial_account.loan_account_no}"
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f"Processed {len(overdue_milestones)} milestones, escalated {escalated_count}.")
                )
                
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [self.lock_id])