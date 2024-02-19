from django.urls import path
from main_app.views import (get_data,download_original_pdf)

urlpatterns = [
    path("all/", get_data, name="get-data"),
    path("download-original-pdf/", download_original_pdf, name="download-original-pdf"),
]
