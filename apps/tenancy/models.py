from django.db import models


class TenantStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"


class Tenant(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=TenantStatus.choices, default=TenantStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class TenantDomain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ("tenant", "domain")

    def __str__(self):
        return f"{self.domain} → {self.tenant.code}"


class TenantSetting(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="settings")
    key = models.CharField(max_length=100)
    value = models.JSONField()

    class Meta:
        unique_together = ("tenant", "key")
