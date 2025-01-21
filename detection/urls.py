from django.urls import path
# from .views import MobileDetectionAPI

from django.urls import path
from .views import MobileDetectionView, SendOTPAPIView, VerifyOTPAPIView, RegistrationAPIView, LoginAPIView

urlpatterns = [
    path('api/mobile-detection/', MobileDetectionView.as_view(), name='mobile-detection'),
    path("api/verify-email/",SendOTPAPIView.as_view(), name="signup"),
    path("api/verify-otp/", VerifyOTPAPIView.as_view(), name="verify-email"),
    path("api/signup/", RegistrationAPIView.as_view(), name="resend-otp"),
    path("api/login/", LoginAPIView.as_view(), name="signin"),
]

