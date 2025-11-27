from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EventViewSet, AuditLogViewSet, UnifiedSearchView, FavoriteViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'events', EventViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('search/', UnifiedSearchView.as_view(), name='unified-search'),
    path('', include(router.urls)),
]
