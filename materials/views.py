from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialPaginator
from materials.serializers import (
    CourseSerializer,
    LessonSerializer,
    CourseDetailSerializer,
)
from users.permissions import (
    IsNotModerator,
    IsOwner,
    IsModeratorOrOwner,
)


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = MaterialPaginator

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsNotModerator()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsOwner()]
        if self.action in ["update", "partial_update", "retrieve"]:
            return [IsAuthenticated(), IsModeratorOrOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Course.objects.all()
        if not self.request.user.groups.filter(name="moders").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsNotModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialPaginator

    def get_queryset(self):
        queryset = Lesson.objects.all()
        if not self.request.user.groups.filter(name="moders").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        queryset = Lesson.objects.all()
        if not self.request.user.groups.filter(name="moders").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        queryset = Lesson.objects.all()
        if not self.request.user.groups.filter(name="moders").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Lesson.objects.all()
        if not self.request.user.groups.filter(name="moders").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response({"error": "Поле course_id обязательно"}, status=400)

        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message})
