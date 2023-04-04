from django.conf import settings
from django.contrib import admin
from django.urls import include, path

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'
handler500 = 'core.views.server_error'

urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace='posts')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
