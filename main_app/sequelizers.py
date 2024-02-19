from main_app.models import AccessModel
from rest_framework import serializers

# from sanvad_project.settings import FILE_SERVE_LINK


class AccessModelSequelizers(serializers.ModelSerializer):

    class Meta:
        model = AccessModel
        fields = "__all__"