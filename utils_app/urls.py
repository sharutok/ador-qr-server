from django.urls import path, include
from utils_app.views import (download_embedded_img, pdf_process,read_text_from_prd,download_orignal_pdf,download_embedded_pdf,)

urlpatterns = [
    path("pdf/process/", pdf_process, name="pdf-process"),
    path("read/text/from/pdf", read_text_from_prd, name="read-text-from-prd"),
    path('download/original/',download_orignal_pdf,name='download-orignal-pdf'),
    path('download/embedded/',download_embedded_pdf,name='download-embedded-pdf'),
]
