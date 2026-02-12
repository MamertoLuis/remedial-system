from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.remedial import models, services


class Command(BaseCommand):
    help = "Rollup next hearing date for legal cases and update reminders."
    lock_id = 280423

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [self.lock_id])
            locked = cursor.fetchone()[0]
            if not locked:
                self.stdout.write(self.style.WARNING("Skipping hearing date rollup: lock already held."))
                return
            try:
                self.stdout.write("Rolling up next hearing dates for legal cases...")
                
                # Get all legal cases that need next hearing date updated
                legal_cases = models.LegalCase.objects.filter(
                    status__in=[models.LegalCaseStatus.ACTIVE, models.LegalCaseStatus.FILED]
                ).select_related("remedial_account")
                
                updated_count = 0
                
                for legal_case in legal_cases:
                    # Get next upcoming hearing
                    next_hearing = models.CourtHearing.objects.filter(
                        legal_case=legal_case,
                        status="scheduled",
                        hearing_date__gte=timezone.now().date()
                    ).order_by("hearing_date").first()
                    
                    if next_hearing:
                        # Update the legal case with next hearing date
                        legal_case.next_hearing_date = next_hearing.hearing_date
                        legal_case.save(update_fields=["next_hearing_date"])
                        updated_count += 1
                        
                        # Check if reminder needs to be sent (7 days before)
                        days_until_hearing = (next_hearing.hearing_date - timezone.now().date()).days
                        
                        if days_until_hearing <= 7 and days_until_hearing >= 0:
                            if not next_hearing.reminder_sent_at:
                                # Send reminder notification
                                rule = models.NotificationRule.objects.filter(
                                    rule_code="HEARING_REMINDER",
                                    status=models.NotificationRuleStatus.ENABLED,
                                ).first()
                                
                                if rule:
                                    recipients = []
                                    if rule.email_to_specific and rule.email_to_specific.email:
                                        recipients.append(rule.email_to_specific.email)
                                    elif rule.email_to_role:
                                        recipients.append(f"{rule.email_to_role}@example.com")
                                    
                                    if recipients:
                                        message = (
                                            f"Upcoming hearing for {legal_case.remedial_account.loan_account_no} "
                                            f"on {next_hearing.hearing_date}"
                                        )
                                        for recipient in recipients:
                                            services.NotificationService.send_notification(
                                                rule,
                                                "CourtHearing",
                                                next_hearing.pk,
                                                recipient,
                                                message,
                                            )
                                        
                                        next_hearing.reminder_sent_at = timezone.now()
                                        next_hearing.save(update_fields=["reminder_sent_at"])
                
                self.stdout.write(
                    self.style.SUCCESS(f"Processed {len(legal_cases)} legal cases, updated {updated_count} next hearing dates.")
                )
                
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [self.lock_id])