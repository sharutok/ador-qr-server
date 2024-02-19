from django.db import models
import uuid
# Create your models here.


class AccessModel(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=True,)
    ref_no=models.AutoField(primary_key=True)
    email_id=models.CharField(max_length=50,default='0')
    file_name=models.CharField(max_length=50,default='0')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta():
        db_table='access_model'