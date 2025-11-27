from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'ConstructOS Django API'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/v1/', include('backend.apps.core.urls')),
    path('api/v1/', include('backend.apps.crm.urls')),
    path('api/v1/', include('backend.apps.erp.urls')),
    path('api/v1/', include('backend.apps.construction.urls')),
    path('api/v1/ai/', include('backend.apps.ai.urls')),
    path('api/v1/chat/', include('backend.apps.chat.urls')),
]
