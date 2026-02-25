from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views as store_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', store_views.home, name='home'),            # Home page
    path('store/', include('store.urls')),              # Store app
    path('carts/', include('carts.urls', namespace='carts')),
    path('accounts/', include('accounts.urls')),        # Accounts app
    path('orders/', include('orders.urls', namespace='orders')),

     
     


]

# ✅ Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
