from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.permissions import IsOwnerOrReadOnly
from users.serializers import UserProfileSerializer, PaymentSerializer, UserSerializer, UserProfilePublicSerializer
from users.models import Payment, User
from users.services import create_stripe_product, create_stripe_price, create_stripe_checkout_session


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
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        return Payment.objects.filter(user=self.request.user)


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        # 1. Создаём продукт и цену в Stripe
        product_id = create_stripe_product(course.title)
        price_id = create_stripe_price(product_id, course.price)  # Предполагается, что у Course есть поле price

        # 2. Создаём сессию оплаты
        success_url = "http://127.0.0.1:8000/users/profile/"
        cancel_url = "http://127.0.0.1:8000/materials/"
        session_data = create_stripe_checkout_session(price_id, success_url, cancel_url)

        # 3. Сохраняем платёж в нашей системе
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            payment_method=Payment.TRANSFER,
            payment_url=session_data["payment_url"],
            stripe_session_id=session_data["session_id"],
        )

        # 4. Возвращаем ссылку на оплату
        return Response({
            "payment_url": payment.payment_url,
            "payment_id": payment.id,
        })
