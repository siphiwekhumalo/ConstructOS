from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EventViewSet, AuditLogViewSet, UnifiedSearchView, FavoriteViewSet, AuthMeView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'events', EventViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('auth/me/', AuthMeView.as_view(), name='auth-me'),
    path('search/', UnifiedSearchView.as_view(), name='unified-search'),
    path('', include(router.urls)),
]
