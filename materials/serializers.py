from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeLinkValidator


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner",)
        validators = [
            YouTubeLinkValidator(field="video_url"),  # <-- укажите ваше поле
        ]


class CourseDetailSerializer(ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    count_lessons_in_course = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    def get_count_lessons_in_course(self, course):
        return course.lessons.count()

    def get_is_subscribed(self, course):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=course).exists()

    class Meta:
        model = Course
        fields = ("title", "description", "lessons", "count_lessons_in_course", "is_subscribed",)


class CourseSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()  # <-- признак подписки

    def get_is_subscribed(self, course):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=course).exists()

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("owner",)
        validators = [
            YouTubeLinkValidator(field="video_url"),
        ]
