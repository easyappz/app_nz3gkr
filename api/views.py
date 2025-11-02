from django.contrib.auth.models import User
from django.db.models import F
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .auth import generate_access_token
from .serializers import (
    MessageSerializer,
    RegisterSerializer,
    LoginSerializer,
    MeSerializer,
    ListingSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    IngestUrlRequestSerializer,
    UserProfileSerializer,
    BlockUserSerializer,
    UnblockUserSerializer,
)
from .models import Listing, Comment, UserProfile, ModerationLog
from .avito import upsert_listing_by_url
from .utils import censor_profanity


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """

    @extend_schema(
        responses={200: MessageSerializer}, description="Get a hello world message"
    )
    def get(self, request):
        data = {"message": "Hello!", "timestamp": timezone.now()}
        serializer = MessageSerializer(data)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="User registered", response=None),
            400: OpenApiResponse(description="Validation error"),
            409: OpenApiResponse(description="Username conflict"),
        },
        description="Register a new user and receive an access token.",
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        email = serializer.validated_data.get("email") or ""

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username is already taken"}, status=status.HTTP_409_CONFLICT)

        user = User.objects.create_user(username=username, password=password, email=email)
        token = generate_access_token(user)
        return Response({"id": user.id, "username": user.username, "token": token}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Authenticated"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Invalid credentials or user blocked"),
        },
        description="Login with username and password to receive an access token.",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "User is blocked"}, status=status.HTTP_401_UNAUTHORIZED)

        token = generate_access_token(user)
        return Response({"id": user.id, "username": user.username, "token": token}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: MeSerializer,
            401: OpenApiResponse(description="Unauthorized"),
        },
        description="Get current user's profile details.",
    )
    def get(self, request):
        user: User = request.user
        # derive block state from profile (preferred) with fallback to is_active
        is_blocked_profile = getattr(user, "profile", None).is_blocked if hasattr(user, "profile") else False
        data = {
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_blocked": is_blocked_profile or (not user.is_active),
        }
        serializer = MeSerializer(data)
        return Response(serializer.data)


# Avitolog endpoints
class ListingsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[],
        responses={200: ListingSerializer(many=True)},
        description="Get most viewed listings ordered by views_count desc. Optional query parameter 'limit' (default 20).",
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 20))
        except Exception:
            limit = 20
        # Hard cap
        if limit < 1:
            limit = 1
        if limit > 50:
            limit = 50
        qs = Listing.objects.all().order_by("-views_count", "-created_at")[:limit]
        return Response(ListingSerializer(qs, many=True).data)


class ListingDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: ListingSerializer, 404: OpenApiResponse(description="Not found")},
        description="Get a listing by id and increment its views_count.",
    )
    def get(self, request, pk: int):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

        Listing.objects.filter(pk=listing.pk).update(views_count=F("views_count") + 1)
        listing.refresh_from_db(fields=["views_count"])
        return Response(ListingSerializer(listing).data)


class IngestUrlView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=IngestUrlRequestSerializer,
        responses={
            200: ListingSerializer,
            201: ListingSerializer,
            400: OpenApiResponse(description="Invalid URL or domain"),
            502: OpenApiResponse(description="Failed to fetch Avito"),
        },
        description=(
            "Create or update listing by Avito URL. If listing exists, refresh base fields. "
            "Only avito.ru domain is allowed."
        ),
    )
    def post(self, request):
        serializer = IngestUrlRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        url = serializer.validated_data["url"].strip()
        try:
            existed = Listing.objects.filter(url=url).exists()
            listing = upsert_listing_by_url(url)
            status_code = status.HTTP_200_OK if existed else status.HTTP_201_CREATED
            return Response(ListingSerializer(listing).data, status=status_code)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Failed to fetch Avito"}, status=status.HTTP_502_BAD_GATEWAY)


class ListingCommentsView(APIView):
    @extend_schema(
        responses={200: CommentSerializer(many=True), 404: OpenApiResponse(description="Listing not found")},
        description="Get comments for a listing (newest first). Deleted comments are excluded.",
    )
    def get(self, request, pk: int):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)
        comments = listing.comments.filter(is_deleted=False).order_by("-created_at")
        return Response(CommentSerializer(comments, many=True).data)

    @extend_schema(
        request=CreateCommentSerializer,
        responses={
            201: CommentSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="User is blocked"),
            404: OpenApiResponse(description="Listing not found"),
        },
        description="Create a comment for a listing. Auth required and user must not be blocked. Profanity is censored.",
    )
    def post(self, request, pk: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile: UserProfile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        if profile.is_blocked:
            return Response({"detail": "User is blocked"}, status=status.HTTP_403_FORBIDDEN)

        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_text = serializer.validated_data["text"]
        filtered_text = censor_profanity(raw_text)
        comment = Comment.objects.create(listing=listing, user=request.user, text=filtered_text)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDeleteView(APIView):
    @extend_schema(
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
        },
        description="Delete a comment (soft delete). Author can delete own comment, staff can delete any. ModerationLog is written.",
    )
    def delete(self, request, comment_id: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        if (comment.user_id != request.user.id) and (not request.user.is_staff):
            return Response({"detail": "You do not have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

        if not comment.is_deleted:
            comment.is_deleted = True
            comment.deleted_by = request.user
            comment.deleted_at = timezone.now()
            comment.save(update_fields=["is_deleted", "deleted_by", "deleted_at"])
            ModerationLog.objects.create(
                actor=request.user,
                action=ModerationLog.ACTION_DELETE_COMMENT,
                target_comment=comment,
                reason=None,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BlockUserSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="User not found"),
        },
        description="Block a user (staff only). Writes ModerationLog.",
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only staff can perform this action"}, status=status.HTTP_403_FORBIDDEN)
        serializer = BlockUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = serializer.validated_data["user_id"]
        reason = serializer.validated_data.get("reason") or ""
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        if not profile.is_blocked:
            profile.is_blocked = True
            profile.blocked_reason = reason or "Blocked via moderation endpoint"
            profile.blocked_at = timezone.now()
            profile.save(update_fields=["is_blocked", "blocked_reason", "blocked_at"])
            ModerationLog.objects.create(
                actor=request.user,
                action=ModerationLog.ACTION_BLOCK_USER,
                target_user=target_user,
                reason=profile.blocked_reason,
            )
        return Response(UserProfileSerializer(profile).data)


class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UnblockUserSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="User not found"),
        },
        description="Unblock a user (staff only).",
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only staff can perform this action"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UnblockUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = serializer.validated_data["user_id"]
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        if profile.is_blocked:
            profile.is_blocked = False
            profile.blocked_at = None
            profile.save(update_fields=["is_blocked", "blocked_at"])
            # Log as block action with an "unblock" reason to avoid changing DB schema
            ModerationLog.objects.create(
                actor=request.user,
                action=ModerationLog.ACTION_BLOCK_USER,
                target_user=target_user,
                reason="unblock",
            )
        return Response(UserProfileSerializer(profile).data)
