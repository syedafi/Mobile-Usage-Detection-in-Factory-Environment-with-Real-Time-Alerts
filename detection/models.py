# from django.db import models

# class MobileDetectionLog(models.Model):
#     timestamp = models.DateTimeField(auto_now_add=True)
#     location = models.aCharField(max_length=100)
#     image = models.ImageField(upload_to='alerts/')
#     alert_message = models.CharField(max_length=255, default='Mobile phone detected!')

#     def __str__(self):
#         return f"{self.timestamp} - {self.location}"

# from django.db import models

# class MobileDetection(models.Model):
#     timestamp = models.DateTimeField()
#     image = models.ImageField(upload_to='screenshots/')
#     detected = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Detection at {self.timestamp}"

from django.db import models

class UploadedVideo(models.Model):
    video = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)  # New field


    def __str__(self):
        return self.username

class OTPVerification(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


