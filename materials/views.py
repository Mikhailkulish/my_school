from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer, CourseDetailSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), ~IsModerator()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsModerator() | IsOwner]
        if self.action in ["update", "partial_update", "retrieve"]:
            return [IsAuthenticated(), IsModerator() | IsOwner]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Course.objects.all()
        if not self.request.user.groups.filter(name="Модератор").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminUser, IsModerator()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def get_queryset(self):
        queryset = Lesson.objects.all()
        if not self.request.user.groups.filter(name="Модератор").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminUser, IsModerator | IsOwner]
