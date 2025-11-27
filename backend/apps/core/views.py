from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Event, AuditLog
from .serializers import UserSerializer, UserCreateSerializer, EventSerializer, AuditLogSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer
