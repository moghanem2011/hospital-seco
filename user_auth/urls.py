from django.urls import path
from . import views
from .views import LoginAPIView, LogoutAPIView, RegisterStepOneAPIView # RegisterStepTwoAPIView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'auth'

urlpatterns = [
   # path('login/', views.LoginAPIView.as_view(), name='user-login'),
   # path('logout/', TokenBlacklistView.as_view(), name='user-logout'),
   # path('signup/doctor/', views.DoctorRegisterView.as_view(), name='doctor-signup'),
   # path('signup/patient/', views.PatientRegisterView.as_view(), name='patient-signup'),
   # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/step1/', RegisterStepOneAPIView.as_view(), name='register-step1'),
    #path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('register/step2/', RegisterStepTwoAPIView.as_view(), name='register-step2'),

]
