from django.http import JsonResponse
from django.urls import path, include

urlpatterns = [
    path('', lambda request: JsonResponse({
        'code': 0,
        'message': 'WMS backend is running',
        'apiBase': '/api/',
    })),
    path('api/', include('api.urls')),
]
