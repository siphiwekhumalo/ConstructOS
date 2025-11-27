"""
URL configuration for Identity/Contact Service API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthMeView, UserViewSet, AccountViewSet, ContactViewSet,
    AddressViewSet, AuditLogViewSet, FavoriteViewSet, EventViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'events', EventViewSet)

urlpatterns = [
    path('auth/me/', AuthMeView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]
