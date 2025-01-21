
import cv2
import torch
import os
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.mail import EmailMessage
from .models import UploadedVideo
from .serializers import VideoUploadSerializer
from django.conf import settings
from datetime import datetime
import base64

import torch
import cv2
import os
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import VideoUploadSerializer
import base64
from django.conf import settings

class MobileDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # 1. Save the uploaded video
        serializer = VideoUploadSerializer(data=request.data)
        if serializer.is_valid():
            video_instance = serializer.save()
            video_path = video_instance.video.path

            # 2. Call the mobile detection function
            detected_frame_path, not_detected_frame_path = self.detect_mobile_phones(video_path)

            # 3. Convert frames to base64 strings
            detected_frame_base64 = self.convert_image_to_base64(detected_frame_path) if detected_frame_path else None
            not_detected_frame_base64 = self.convert_image_to_base64(not_detected_frame_path) if not_detected_frame_path else None

            response_data = {
                'message': 'Processing complete.',
                'detected_frame': detected_frame_base64,
                'not_detected_frame': not_detected_frame_base64
            }

            return Response(response_data)
        else:
            return Response(serializer.errors, status=400)

    def detect_mobile_phones(self, video_path):
        # Load YOLO model (you can replace with any custom model you want)
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

        cap = cv2.VideoCapture(video_path)
        detected_frame_path = None
        not_detected_frame_path = None
        frame_count = 0
        target_time = 13  # Set the target time for capturing 'not detected' frame (in seconds)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            timestamp = self.get_frame_timestamp(cap)
            current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)  # Current time in seconds

            if frame_count % 30 == 0:  # Process every 30th frame
                results = model(frame)
                detections = results.pandas().xyxy[0]

                if 'cell phone' in detections['name'].values:
                    # Draw bounding boxes for detected objects
                    for i, row in detections.iterrows():
                        if row['name'] == 'cell phone':
                            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                            color = (0, 255, 0)  # Green box for detected mobile
                            label = f'Mobile Detected {timestamp}'
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    # Save frame with detected phone and timestamp
                    detected_frame_path = self.save_frame_with_unique_name(frame, 'detected_frame')
                else:
                    # Capture the "not detected" frame at exactly 13 seconds
                    if current_time == target_time and not_detected_frame_path is None:
                        label = f'No Mobile Detected {timestamp}'
                        cv2.putText(frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Red text

                        # Save frame without drawing any bounding boxes for detected mobile phones
                        not_detected_frame_path = self.save_frame_with_unique_name(frame, 'not_detected_frame', save_detected=False)

                if detected_frame_path and not_detected_frame_path:
                    break  # Stop processing once we have both images

        cap.release()
        return detected_frame_path, not_detected_frame_path


    def save_frame_with_unique_name(self, frame, prefix, save_detected=True):
        """ Save frame with a unique name that includes a timestamp. Optionally save without bounding boxes for 'not detected' frames. """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.jpg"
        save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Ensure directory exists
        
        if save_detected:
            cv2.imwrite(save_path, frame)  # Save the frame with bounding boxes (for detected frames)
        else:
            # Create a copy of the frame and save it without any bounding boxes (for not detected frames)
            frame_copy = frame.copy()
            cv2.imwrite(save_path, frame_copy)  # Save the frame without bounding boxes (for not detected frames)
            
        return save_path


    def get_frame_timestamp(self, cap):
        """ Get the current timestamp of the video in HH:MM:SS format """
        current_millis = cap.get(cv2.CAP_PROP_POS_MSEC)
        total_seconds = int(current_millis // 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def convert_image_to_base64(self, image_path):
        """ Convert an image file to a base64 string """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, OTPVerification
from .utils import generate_otp, send_otp_email
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User  # Assuming you're using Django's default User model

from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTPVerification
from .utils import send_otp_email, generate_otp  # Replace with your actual utility functions


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import re  # For regex validation
from .models import OTPVerification
from .utils import generate_otp, send_otp_email


class SendOTPAPIView(APIView):
    """Send OTP for email verification."""

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Dynamically get the User model
        User = get_user_model()

        # Check if the email exists in the system (optional logic)
        user = User.objects.filter(email=email).first()
        if user and user.is_registered:
            return Response({"message": "User is already registered. Please login."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate and send OTP regardless of verification status
        otp = generate_otp()
        OTPVerification.objects.update_or_create(email=email, defaults={'otp': otp})
        send_otp_email(email, otp)

        # Inform the user that OTP has been sent
        return Response({"message": "OTP has been sent to your email. Please verify it."},
                        status=status.HTTP_200_OK)






from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTPVerification
from .utils import send_otp_email, generate_otp  # Replace with your actual utility functions

class VerifyOTPAPIView(APIView):
    """Verify OTP and allow user to complete registration."""

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_record = OTPVerification.objects.get(email=email)

            if otp_record.otp != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            User = get_user_model()
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": get_random_string(8)}
            )
            user.is_verified = True
            user.save()

            otp_record.delete()

            return Response({"message": "Email has been verified. You can now register your account."},
                            status=200)

        except OTPVerification.DoesNotExist:
            return Response({"error": "Email not found or OTP expired."}, status=status.HTTP_400_BAD_REQUEST)






import re
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User  # Update this to your custom User model if you're using one


import re
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response

class RegistrationAPIView(APIView):
    """Complete registration after OTP verification."""

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        phone_number = request.data.get('phone_number')
        organization = request.data.get('organization')

        # Validate phone number
        if not re.match(r'^\d{10}$', phone_number):
            return Response({"error": "Phone number must be a valid 10-digit number."}, status=400)

        # Check if passwords match
        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        # Get the custom user model dynamically
        User = get_user_model()

        # Check if the user is already registered using email
        user = User.objects.filter(email=email).first()
        if user:
            if user.is_registered:  # Assuming `is_registered` indicates the user has completed registration
                return Response({"error": "User is already registered. Please login."}, status=400)
            else:
                # If the user exists but is not fully registered, allow them to complete registration
                if not user.is_verified:
                    return Response({"error": "Email verification is required."}, status=400)

                # Check if the username is already taken by another user
                if User.objects.filter(username=username).exclude(email=email).exists():
                    return Response({"error": "User with that username already exists."}, status=400)

                # Update user details
                user.username = username
                user.set_password(password)
                user.phone_number = phone_number
                user.organization = organization
                user.is_registered = True  # Mark the user as fully registered
                user.save()

                return Response({"message": "Account successfully registered. Please login."}, status=201)
        
        # Check if the username is already taken by another user (if the user does not exist by email)
        if User.objects.filter(username=username).exists():
            return Response({"error": "User with that username already exists."}, status=400)

        # If the user does not exist at all, send an error response
        return Response({"error": "Email verification is required."}, status=400)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class LoginAPIView(APIView):
    """Authenticate and log in the user."""

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful.",
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)





