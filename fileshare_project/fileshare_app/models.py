from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    USER_TYPE_CHOICES = [
        ('OPS', 'Operation User'),
        ('CLIENT', 'Client User')
    ]
    user_type = models.CharField(max_length=6, choices=USER_TYPE_CHOICES)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class File(models.Model):
    ALLOWED_EXTENSIONS = ['pptx', 'docx', 'xlsx']

    name = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='uploads/')  
    uploaded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.uploaded_file.name.split('.')[-1] in self.ALLOWED_EXTENSIONS:
            raise ValueError('Invalid file format.')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class UploadedFile(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
