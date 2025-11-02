from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Listing(models.Model):
    url = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=255)
    image_url = models.URLField(max_length=1000, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-views_count", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title}"


class Comment(models.Model):
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_comments",
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Comment #{self.pk} by {self.user} on {self.listing}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.CharField(max_length=255, null=True, blank=True)
    blocked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Profile of {self.user}"


class BannedWord(models.Model):
    word = models.CharField(max_length=128, unique=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.word:
            self.word = self.word.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.word


class ModerationLog(models.Model):
    ACTION_DELETE_COMMENT = "delete_comment"
    ACTION_BLOCK_USER = "block_user"

    ACTION_CHOICES = (
        (ACTION_DELETE_COMMENT, "Delete comment"),
        (ACTION_BLOCK_USER, "Block user"),
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderation_actions",
    )
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    target_comment = models.ForeignKey(
        "Comment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderation_logs",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderation_logs",
    )
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_action_display()} by {self.actor} at {self.created_at:%Y-%m-%d %H:%M:%S}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
