from rest_framework.serializers import ModelSerializer

from users.models import User


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "city", "avatar")
        read_only_fields = ("email",)
