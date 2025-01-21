from rest_framework import serializers
from .models import UploadedVideo

class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedVideo
        fields = ['video']
