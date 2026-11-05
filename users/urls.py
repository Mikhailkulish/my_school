from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import UserProfileAPIView, PaymentViewSet, UserCreateAPIView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
]

urlpatterns += router.urls
