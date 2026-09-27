from django.conf import settings
from django.db import models


# ─────────────────────────────────────────────────────────────────────────────
# Custom / bulk client emails — sent from the admin dashboard via Resend, using
# the same branded template as app.email_service.
# ─────────────────────────────────────────────────────────────────────────────

class EmailCampaign(models.Model):
    """A record of a custom email composed and sent to one or more clients."""

    subject         = models.CharField(max_length=255)
    heading         = models.CharField(max_length=255, blank=True, default="")
    message         = models.TextField()
    cta_text        = models.CharField(max_length=100, blank=True, default="")
    cta_url         = models.URLField(blank=True, default="")
    social_links    = models.JSONField(blank=True, default=dict)

    recipient_count = models.PositiveIntegerField(default=0)
    sent_count      = models.PositiveIntegerField(default=0)
    failed_count    = models.PositiveIntegerField(default=0)

    sent_by         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+",
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.sent_count}/{self.recipient_count})"


class EmailCampaignRecipient(models.Model):
    """One recipient of an EmailCampaign, with its own delivery outcome."""

    STATUS_CHOICES = [
        ("sent",   "Sent"),
        ("failed", "Failed"),
    ]

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name="recipients")
    user     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+",
    )
    # Snapshot of the recipient's identity at send time, so history survives
    # even if the user account is later edited or deleted.
    email    = models.EmailField()
    name     = models.CharField(max_length=255, blank=True, default="")
    status   = models.CharField(max_length=10, choices=STATUS_CHOICES, default="sent")

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return f"{self.email} — {self.status}"
