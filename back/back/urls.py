from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

def health_check(request):
    """Simple health check endpoint"""
    return HttpResponse("OK", content_type="text/plain")

def api_info(request):
    """API information endpoint"""
    return HttpResponse(
        f"Real Estate Auction API - Environment: {getattr(settings, 'ENVIRONMENT', 'development')}",
        content_type="text/plain"
    )

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    path('', api_info, name='api_info'),
    
    # Admin with custom URL (configurable via settings)
    path(getattr(settings, 'ADMIN_URL', 'admin/'), admin.site.urls),
    
    # API endpoints
    path('api/', include('base.urls')),
    path('api/accounts/', include('accounts.urls')),
    
    # Redirect root to API info
    path('api/', RedirectView.as_view(url='/api/properties/', permanent=False), name='api_root'),
]

# Error handlers
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
handler403 = 'django.views.defaults.permission_denied'
handler400 = 'django.views.defaults.bad_request'

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar (if installed)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
else:
    # Production: serve media files (static files handled by whitenoise)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)