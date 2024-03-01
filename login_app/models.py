from django.db import models
import uuid

class AdminUsers(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4, editable=True)
    user=models.CharField(max_length=150, null=True)
    emp_id=models.CharField(max_length=150, null=True)
    file_upload_type=models.CharField(max_length=150, null=True)
    password=models.CharField(max_length=300, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='admin_users'