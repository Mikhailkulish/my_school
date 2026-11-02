from django.urls import path
from rest_framework.routers import SimpleRouter

from users.views import UserProfileAPIView, PaymentViewSet

app_name = "users"

router = SimpleRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
]

urlpatterns += router.urls
