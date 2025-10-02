from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views as store_views

urlpatterns = [
     path('admin/', admin.site.urls),
    path('', store_views.home, name='home'),  # root URL
    path('home/', store_views.store, name='home_page'),  # /home URL
    path('store/', include('store.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
