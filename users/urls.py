from django.urls import path

from users.views import UserProfileAPIView

app_name = "users"

urlpatterns = [
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
]
