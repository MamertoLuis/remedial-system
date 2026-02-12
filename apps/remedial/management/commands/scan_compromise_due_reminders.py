import logging

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.remedial import models, services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send compromise due reminders based on notification rules."
    lock_id = 280420

    def handle(self, *args, **options):
        rule = models.NotificationRule.objects.filter(
            rule_code="COMPROMISE_DUE_REMINDER",
            status=models.NotificationRuleStatus.ENABLED,
        ).first()
        if not rule or not rule.days_before:
            self.stdout.write(self.style.WARNING("Due reminder rule not configured."))
            return
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [self.lock_id])
            locked = cursor.fetchone()[0]
            if not locked:
                self.stdout.write(self.style.WARNING("Skipping reminder scan: lock held."))
                return
            try:
                target_date = timezone.now().date() + timezone.timedelta(days=rule.days_before)
                items = models.CompromiseScheduleItem.objects.filter(
                    due_date=target_date,
                    status=models.ScheduleStatus.DUE,
                ).select_related("compromise_agreement")
                for item in items:
                    recipients = []
                    if rule.email_to_specific and rule.email_to_specific.email:
                        recipients.append(rule.email_to_specific.email)
                    elif rule.email_to_role:
                        recipients.append(f"{rule.email_to_role}@example.com")
                    if not recipients:
                        continue
                    message = (
                        f"{item.compromise_agreement.remedial_account.loan_account_no} "
                        f"payment due on {item.due_date}"
                    )
                    for recipient in recipients:
                        services.send_notification(
                            rule,
                            "CompromiseScheduleItem",
                            item.pk,
                            recipient,
                            message,
                        )
                    item.last_reminder_sent_at = timezone.now()
                    item.save(update_fields=["last_reminder_sent_at"])
                self.stdout.write(self.style.SUCCESS("Due reminders processed."))
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [self.lock_id])
