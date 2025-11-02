from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Listing, Comment, UserProfile


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    timestamp = serializers.DateTimeField(read_only=True)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_blocked = serializers.BooleanField(read_only=True)


# Avitolog serializers
class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = (
            "id",
            "url",
            "title",
            "image_url",
            "price",
            "description",
            "published_at",
            "views_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "listing",
            "user_id",
            "user_username",
            "text",
            "created_at",
        )
        read_only_fields = ("id", "listing", "user_id", "user_username", "created_at")


class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=False, max_length=5000)


class IngestUrlRequestSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=500)


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = ("user_id", "username", "is_blocked", "blocked_reason", "blocked_at")
        read_only_fields = ("user_id", "username", "blocked_at")


class BlockUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    reason = serializers.CharField(allow_blank=True, required=False)


class UnblockUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
