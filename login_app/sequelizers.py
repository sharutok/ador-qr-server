from rest_framework import serializers
from login_app.models import AdminUsers

class AdminUsersSerializers(serializers.ModelSerializer):

    class Meta:
        model= AdminUsers
        fields= "__all__"
