from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/',include('main_app.urls')),
    path('utils/',include('utils_app.urls')),
    path('user/',include('login_app.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


