from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.serializers import UserProfileSerializer, PaymentSerializer, UserSerializer
from users.models import Payment, User


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


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
