from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, EventViewSet, AuditLogViewSet, UnifiedSearchView, 
    FavoriteViewSet, AuthMeView, HealthCheckView, CacheStatsView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'events', EventViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('auth/me/', AuthMeView.as_view(), name='auth-me'),
    path('search/', UnifiedSearchView.as_view(), name='unified-search'),
    path('health/liveness/', HealthCheckView.as_view(), {'check_type': 'liveness'}, name='health-liveness'),
    path('health/readiness/', HealthCheckView.as_view(), {'check_type': 'readiness'}, name='health-readiness'),
    path('cache/stats/', CacheStatsView.as_view(), name='cache-stats'),
    path('', include(router.urls)),
]
