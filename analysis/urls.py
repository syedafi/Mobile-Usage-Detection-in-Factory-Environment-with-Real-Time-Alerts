
# main urls.py

from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('detection.urls')),  # Include your app's URLs
# ]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('detection.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


