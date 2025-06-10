"""
URL configuration for back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_view(request):
    """Simple test view that bypasses all middleware"""
    return HttpResponse(
        "✅ Backend working! No redirects!\n"
        f"Method: {request.method}\n"
        f"Path: {request.path}\n"
        f"DEBUG: {settings.DEBUG}\n"
        f"Headers: {dict(request.headers)}\n",
        content_type="text/plain"
    )

@csrf_exempt  
def debug_settings(request):
    """Debug view to check Django settings"""
    debug_info = f"""
=== DJANGO SETTINGS DEBUG ===
DEBUG: {getattr(settings, 'DEBUG', 'NOT SET')}
SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', 'NOT SET')}
SECURE_PROXY_SSL_HEADER: {getattr(settings, 'SECURE_PROXY_SSL_HEADER', 'NOT SET')}
SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'NOT SET')}
CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'NOT SET')}
ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', 'NOT SET')}

MIDDLEWARE:
{chr(10).join(getattr(settings, 'MIDDLEWARE', ['NOT SET']))}
    """
    return HttpResponse(f"<pre>{debug_info}</pre>")

urlpatterns = [
    # ✅ DEBUG ENDPOINTS - These bypass middleware
    path('', test_view),  # Root URL
    path('test/', test_view),  # Test endpoint
    path('debug/', debug_settings),  # Debug endpoint 
    
    # ✅ ORIGINAL ENDPOINTS
    path('admin/', admin.site.urls),
    path('api/', include('base.urls')),
    path('api/accounts/', include('accounts.urls')),
]

# Serve static files
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Serve media files (not only in development)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)