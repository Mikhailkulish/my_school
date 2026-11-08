from rest_framework.serializers import ModelSerializer

from users.models import User, Payment
from materials.serializers import CourseSerializer, LessonSerializer


class PaymentSerializer(ModelSerializer):
    course_data = CourseSerializer(source="course", read_only=True)
    lesson_data = LessonSerializer(source="lesson", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "payment_date",
            "course",
            "lesson",
            "amount",
            "payment_method",
            "course_data",
            "lesson_data",
        )


class UserProfilePublicSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "phone", "city", "avatar")


class UserProfileSerializer(ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payments",
        )
        read_only_fields = ("email",)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar"
        )
        extra_kwargs = {"password": {"write_only": True}}
