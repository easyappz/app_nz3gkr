from django.contrib import admin
from django.utils import timezone

from .models import Listing, Comment, UserProfile, BannedWord, ModerationLog


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "url",
        "price",
        "published_at",
        "views_count",
        "created_at",
    )
    search_fields = ("title", "url")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
    ordering = ("-views_count", "-created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "is_deleted", "created_at")
    list_filter = ("is_deleted",)
    search_fields = ("text",)
    raw_id_fields = ("listing", "user", "deleted_by")
    date_hierarchy = "created_at"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_blocked", "blocked_at")
    list_filter = ("is_blocked",)
    search_fields = ("user__username", "user__email")
    actions = ("block_users", "unblock_users")

    @admin.action(description="Block selected users")
    def block_users(self, request, queryset):
        updated = 0
        for profile in queryset.select_related("user"):
            if not profile.is_blocked:
                profile.is_blocked = True
                profile.blocked_at = timezone.now()
                if not profile.blocked_reason:
                    profile.blocked_reason = "Blocked via admin action"
                profile.save(update_fields=["is_blocked", "blocked_at", "blocked_reason"])
                ModerationLog.objects.create(
                    actor=request.user,
                    action=ModerationLog.ACTION_BLOCK_USER,
                    target_user=profile.user,
                    reason=profile.blocked_reason or "Blocked via admin action",
                )
                updated += 1
        self.message_user(request, f"Blocked {updated} user(s)")

    @admin.action(description="Unblock selected users")
    def unblock_users(self, request, queryset):
        updated = 0
        for profile in queryset:
            if profile.is_blocked:
                profile.is_blocked = False
                profile.blocked_at = None
                # keep last reason for audit trail
                profile.save(update_fields=["is_blocked", "blocked_at"])
                updated += 1
        self.message_user(request, f"Unblocked {updated} user(s)")


@admin.register(BannedWord)
class BannedWordAdmin(admin.ModelAdmin):
    list_display = ("word", "is_active")
    list_filter = ("is_active",)
    search_fields = ("word",)


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "created_at")
    list_filter = ("action",)
    search_fields = ("reason", "actor__username", "target_user__username")
    readonly_fields = (
        "actor",
        "action",
        "target_comment",
        "target_user",
        "reason",
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
