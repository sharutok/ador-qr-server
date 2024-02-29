from django.db import models
import uuid

def upload_original_qr_pdf(instance, filename):
    return "/".join(["qr-code-test-certificate-inhouse-original-pdf", str(instance.id), filename])



class FileUploadPDF(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4, editable=True,)    
    pdf_loc = models.FileField(blank=True, null=True, upload_to=upload_original_qr_pdf)
    batch_number=models.CharField(max_length=50, null=True)
    file_type=models.CharField(max_length=50, null=True)
    file_name = models.CharField(max_length=50, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.batch_number
    
    class Meta:
        db_table='file_data'