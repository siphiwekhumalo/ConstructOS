from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, EventViewSet, AuditLogViewSet, UnifiedSearchView, 
    FavoriteViewSet, AuthMeView, HealthCheckView, CacheStatsView
)
from .auth_views import (
    login_view, logout_view, current_user_view,
    demo_users_view, quick_login_view, setup_demo_users_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'events', EventViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('auth/login/', login_view, name='auth-login'),
    path('auth/logout/', logout_view, name='auth-logout'),
    path('auth/me/', current_user_view, name='auth-current-user'),
    path('auth/demo-users/', demo_users_view, name='auth-demo-users'),
    path('auth/quick-login/', quick_login_view, name='auth-quick-login'),
    path('auth/setup-demo/', setup_demo_users_view, name='auth-setup-demo'),
    path('search/', UnifiedSearchView.as_view(), name='unified-search'),
    path('health/liveness/', HealthCheckView.as_view(), {'check_type': 'liveness'}, name='health-liveness'),
    path('health/readiness/', HealthCheckView.as_view(), {'check_type': 'readiness'}, name='health-readiness'),
    path('cache/stats/', CacheStatsView.as_view(), name='cache-stats'),
    path('', include(router.urls)),
]
