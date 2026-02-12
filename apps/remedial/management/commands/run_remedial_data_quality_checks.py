from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.remedial import models, services


class Command(BaseCommand):
    help = "Run comprehensive data quality checks for remedial system."
    lock_id = 280424

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [self.lock_id])
            locked = cursor.fetchone()[0]
            if not locked:
                self.stdout.write(self.style.WARNING("Skipping data quality check: lock already held."))
                return
            try:
                self.stdout.write("Running comprehensive data quality checks...")
                
                issues_found = []
                total_issues = 0
                
                # Check 1: Missing borrower names
                missing_borrowers = services.DataQualityService.run_data_quality_checks(None)
                for issue in missing_borrowers:
                    issues_found.append(f"Missing borrower names: {issue['count']} accounts")
                    total_issues += issue['count']
                
                # Check 2: Inconsistent compromise totals
                inconsistent_compromises = models.CompromiseAgreement.objects.annotate(
                    total_scheduled=models.Sum(
                        'schedule_items__amount_due',
                        filter=models.Q(schedule_items__amount_due__isnull=False)
                    )
                ).filter(
                    total_scheduled__isnull=False,
                    total_scheduled__gt=models.F('settlement_amount')
                )
                
                if inconsistent_compromises.exists():
                    count = inconsistent_compromises.count()
                    issues_found.append(f"Inconsistent compromise totals: {count} agreements")
                    total_issues += count
                    
                    for compromise in inconsistent_compromises[:5]:  # Show first 5 examples
                        self.stdout.write(
                            f"  - Agreement {compromise.agreement_no}: "
                            f"Scheduled {compromise.total_scheduled} vs Settlement {compromise.settlement_amount}"
                        )
                
                # Check 3: Compromises without active accounts
                orphaned_compromises = models.CompromiseAgreement.objects.filter(
                    remedial_account__isnull=True
                )
                if orphaned_compromises.exists():
                    count = orphaned_compromises.count()
                    issues_found.append(f"Orphaned compromises: {count} agreements")
                    total_issues += count
                
                # Check 4: Legal cases without active accounts
                orphaned_cases = models.LegalCase.objects.filter(
                    remedial_account__isnull=True
                )
                if orphaned_cases.exists():
                    count = orphaned_cases.count()
                    issues_found.append(f"Orphaned legal cases: {count} cases")
                    total_issues += count
                
                # Check 5: Recovery actions without proper account stage
                misstaged_actions = models.RecoveryAction.objects.filter(
                    remedial_account__stage__in=[
                        models.RemedialStage.COMPROMISE,
                        models.RemedialStage.CLOSED,
                        models.RemedialStage.WRITE_OFF
                    ]
                )
                if misstaged_actions.exists():
                    count = misstaged_actions.count()
                    issues_found.append(f"Misstaged recovery actions: {count} actions")
                    total_issues += count
                
                # Check 6: Documents with invalid entities
                invalid_docs = models.RemedialDocument.objects.filter(
                    models.Q(entity_type='remedial_account') & models.Q(entity_id__isnull=True) |
                    models.Q(entity_type='compromise_agreement') & models.Q(entity_id__isnull=True) |
                    models.Q(entity_type='legal_case') & models.Q(entity_id__isnull=True) |
                    models.Q(entity_type='recovery_action') & models.Q(entity_id__isnull=True)
                )
                if invalid_docs.exists():
                    count = invalid_docs.count()
                    issues_found.append(f"Invalid document entities: {count} documents")
                    total_issues += count
                
                # Check 7: Overdue payments not marked as overdue
                overdue_payments = models.CompromiseScheduleItem.objects.filter(
                    status=models.ScheduleStatus.DUE,
                    due_date__lt=timezone.now().date() - timezone.timedelta(days=3)
                )
                if overdue_payments.exists():
                    count = overdue_payments.count()
                    issues_found.append(f"Overdue payments not marked: {count} items")
                    total_issues += count
                
                # Check 8: Multiple active compromises per account
                active_compromises_per_account = models.CompromiseAgreement.objects.filter(
                    status__in=[models.CompromiseStatus.APPROVED, models.CompromiseStatus.ACTIVE]
                ).values('remedial_account').annotate(
                    count=models.Count('id')
                ).filter(count__gt=1)
                
                if active_compromises_per_account.exists():
                    count = active_compromises_per_account.count()
                    issues_found.append(f"Multiple active compromises: {count} accounts")
                    total_issues += count
                
                # Summary report
                self.stdout.write("\n" + "="*50)
                self.stdout.write("DATA QUALITY SUMMARY")
                self.stdout.write("="*50)
                
                if issues_found:
                    self.stdout.write(self.style.WARNING(f"Found {total_issues} data quality issues:"))
                    for issue in issues_found:
                        self.stdout.write(f"  - {issue}")
                else:
                    self.stdout.write(self.style.SUCCESS("No data quality issues found."))
                
                # Recommendations
                self.stdout.write("\nRECOMMENDATIONS:")
                if inconsistent_compromises.exists():
                    self.stdout.write("  - Review and adjust settlement amounts for inconsistent compromises")
                if orphaned_compromises.exists():
                    self.stdout.write("  - Delete or reassign orphaned compromise agreements")
                if misstaged_actions.exists():
                    self.stdout.write("  - Update account stages to match recovery action types")
                if overdue_payments.exists():
                    self.stdout.write("  - Mark overdue payments and trigger escalation process")
                
                self.stdout.write("\nData quality check completed.")
                
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [self.lock_id])