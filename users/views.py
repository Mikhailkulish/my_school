import stripe
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, filters, status as http_status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from materials.models import Course
from users.permissions import IsOwnerOrReadOnly
from users.serializers import UserProfileSerializer, PaymentSerializer, UserSerializer, UserProfilePublicSerializer, \
    PaymentStatusResponseSerializer
from users.models import Payment, User
from users.services import create_stripe_product, create_stripe_price, create_stripe_checkout_session, \
    retrieve_stripe_session


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
        if not course_id:
            return Response(
                {"error": "Поле 'course_id' обязательно."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)

        # Проверка наличия ключа Stripe
        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {"error": "Stripe не настроен (отсутствует STRIPE_SECRET_KEY)."},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            product_id = create_stripe_product(course.title)
            price_id = create_stripe_price(product_id, course.price)
            success_url = "http://127.0.0.1:8000/users/payment/profile/"
            cancel_url = "http://127.0.0.1:8000/users/payment/materials/"
            session_data = create_stripe_checkout_session(price_id, success_url, cancel_url)

            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                payment_method=Payment.TRANSFER,
                payment_url=session_data["payment_url"],
                stripe_session_id=session_data["session_id"],
                status=Payment.PENDING,
            )

            return Response(
                {
                    "payment_url": payment.payment_url,
                    "payment_id": payment.id,
                    "status": payment.status,
                },
                status=http_status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Ошибка Stripe: {str(e)}"},
                status=http_status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            return Response(
                {"error": f"Внутренняя ошибка: {str(e)}"},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PaymentStatusView(APIView):
    """
    GET /users/payments/<id>/status/
    Запрашивает статус платежа в Stripe и обновляет его в нашей БД.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: PaymentStatusResponseSerializer,
            400: "Bad Request",
            404: "Not Found",
            502: "Stripe Error",
        },
        operation_description="Проверяет статус платежа в Stripe и обновляет его в БД.",
        manual_parameters=[
            openapi.Parameter(
                "payment_id",
                openapi.IN_PATH,
                description="ID платежа",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )

    def get(self, request, payment_id, *args, **kwargs):
        # 1. Находим платёж, принадлежащий текущему пользователю
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        # 2. Проверяем, что у платежа есть stripe_session_id
        if not payment.stripe_session_id:
            return Response(
                {"error": "У этого платежа нет сессии Stripe."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        # 3. Запрашиваем статус в Stripe
        try:
            session = retrieve_stripe_session(payment.stripe_session_id)
        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Ошибка Stripe: {str(e)}"},
                status=http_status.HTTP_502_BAD_GATEWAY,
            )

        # 4. Маппинг статусов Stripe -> наши статусы
        status_map = {
            "paid": Payment.PAID,
            "unpaid": Payment.PENDING,
            "no_payment_required": Payment.PAID,
        }
        new_status = status_map.get(session.payment_status, Payment.PENDING)

        # 5. Обновляем статус в БД, если он изменился
        if payment.status != new_status:
            payment.status = new_status
            payment.save(update_fields=["status"])

        # 6. Возвращаем клиенту информацию
        return Response(
            {
                "payment_id": payment.id,
                "status": payment.status,
                "stripe_payment_status": session.payment_status,
                "amount": payment.amount,
            },
            status=http_status.HTTP_200_OK,
        )
