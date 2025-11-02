from django.urls import path
from .views import (
    HelloView,
    RegisterView,
    LoginView,
    MeView,
    ListingsView,
    ListingDetailView,
    IngestUrlView,
    ListingCommentsView,
    CommentDeleteView,
    BlockUserView,
    UnblockUserView,
)

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),

    # Auth
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/me", MeView.as_view(), name="auth-me"),

    # Listings
    path("listings/", ListingsView.as_view(), name="listings-popular"),
    path("listings/ingest-url/", IngestUrlView.as_view(), name="listings-ingest-url"),
    path("listings/<int:pk>/", ListingDetailView.as_view(), name="listing-detail"),

    # Comments
    path("listings/<int:pk>/comments/", ListingCommentsView.as_view(), name="listing-comments"),
    path("comments/<int:comment_id>/", CommentDeleteView.as_view(), name="comment-delete"),

    # Moderation
    path("moderation/block-user/", BlockUserView.as_view(), name="moderation-block-user"),
    path("moderation/unblock-user/", UnblockUserView.as_view(), name="moderation-unblock-user"),
]
