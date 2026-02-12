from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.remedial import models, services


class Command(BaseCommand):
    help = "Send reminders for upcoming court hearings."
    lock_id = 280421

    def handle(self, *args, **options):
        rule = models.NotificationRule.objects.filter(
            rule_code="HEARING_REMINDER",
            status=models.NotificationRuleStatus.ENABLED,
        ).first()
        if not rule or not rule.days_before:
            self.stdout.write(self.style.WARNING("Hearing reminder rule not configured."))
            return
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [self.lock_id])
            if not cursor.fetchone()[0]:
                self.stdout.write(self.style.WARNING("Skipping hearing scan: lock held."))
                return
            try:
                target_date = timezone.now().date() + timezone.timedelta(days=rule.days_before)
                hearings = models.CourtHearing.objects.filter(
                    hearing_date=target_date,
                    status="scheduled",
                ).select_related("legal_case")
                for hearing in hearings:
                    recipients = []
                    if rule.email_to_specific and rule.email_to_specific.email:
                        recipients.append(rule.email_to_specific.email)
                    elif rule.email_to_role:
                        recipients.append(f"{rule.email_to_role}@example.com")
                    message = (
                        f"Hearing for {hearing.legal_case.remedial_account.loan_account_no} on {hearing.hearing_date}"
                    )
                    for recipient in recipients:
                        services.send_notification(
                            rule,
                            "CourtHearing",
                            hearing.pk,
                            recipient,
                            message,
                        )
                    hearing.reminder_sent_at = timezone.now()
                    hearing.save(update_fields=["reminder_sent_at"])
                self.stdout.write(self.style.SUCCESS("Hearing reminders processed."))
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [self.lock_id])
