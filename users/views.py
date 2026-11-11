from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import IsOwnerOrReadOnly
from users.serializers import UserProfileSerializer, PaymentSerializer, UserSerializer, UserProfilePublicSerializer
from users.models import Payment, User


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(serializer.validated_data["password"])
        user.save()


class UserProfileAPIView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileSerializer
        if self.get_object() == self.request.user:
            return UserProfileSerializer
        return UserProfilePublicSerializer

    def get_object(self):
        pk = self.kwargs.get("pk")
        obj = User.objects.get(pk=pk) if pk else self.request.user
        self.check_object_permissions(self.request, obj)
        return obj


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = ['course', 'lesson', 'payment_method']

    ordering_fields = ['payment_date']

    ordering = ['-payment_date']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
