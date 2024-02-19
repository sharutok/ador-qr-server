from utils_app.models import FileUploadPDF
from rest_framework import serializers


class FileUploadPDFSequelizers(serializers.ModelSerializer):

    class Meta:
        model = FileUploadPDF
        fields = "__all__"