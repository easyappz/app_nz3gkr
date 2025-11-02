from django.contrib.auth.models import User
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
)


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

        # Extra conflict handling (in addition to serializer validation) to return 409
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
        data = {
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            # is_blocked derived from is_active
            "is_blocked": not user.is_active,
        }
        serializer = MeSerializer(data)
        return Response(serializer.data)
