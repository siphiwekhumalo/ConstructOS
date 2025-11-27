from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, EventViewSet, AuditLogViewSet, UnifiedSearchView, 
    FavoriteViewSet, AuthMeView, HealthCheckView, CacheStatsView,
    SecurityEventsView, SecurityDashboardView, ForceLogoutView,
    DashboardFinanceSummaryView, DashboardARDaysView, DashboardProfitMarginView,
    DashboardCashFlowView, DashboardTrendChartView, DashboardReworkCostView,
    DashboardSafetySummaryView, DashboardSPIMapView, DashboardResourceUtilizationView,
    DashboardProjectMapView
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
    path('security/events/', SecurityEventsView.as_view(), name='security-events'),
    path('security/dashboard/', SecurityDashboardView.as_view(), name='security-dashboard'),
    path('security/force-logout/', ForceLogoutView.as_view(), name='security-force-logout'),
    path('dashboard/finance-summary/', DashboardFinanceSummaryView.as_view(), name='dashboard-finance-summary'),
    path('dashboard/ar-days/', DashboardARDaysView.as_view(), name='dashboard-ar-days'),
    path('dashboard/profit-margin/', DashboardProfitMarginView.as_view(), name='dashboard-profit-margin'),
    path('dashboard/cash-flow/', DashboardCashFlowView.as_view(), name='dashboard-cash-flow'),
    path('dashboard/trend-chart/', DashboardTrendChartView.as_view(), name='dashboard-trend-chart'),
    path('dashboard/rework-cost/', DashboardReworkCostView.as_view(), name='dashboard-rework-cost'),
    path('dashboard/safety-summary/', DashboardSafetySummaryView.as_view(), name='dashboard-safety-summary'),
    path('dashboard/spi-map/', DashboardSPIMapView.as_view(), name='dashboard-spi-map'),
    path('dashboard/resource-utilization/', DashboardResourceUtilizationView.as_view(), name='dashboard-resource-utilization'),
    path('dashboard/project-map/', DashboardProjectMapView.as_view(), name='dashboard-project-map'),
    path('', include(router.urls)),
]
