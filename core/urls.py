from django.urls import path
from . import views


urlpatterns = [
    path("doctors/", views.DoctorList.as_view()),
    path("doctor/<int:pk>", views.DoctorDetail.as_view()),
    path("managment/", views.ManagmentList.as_view()),
    # path("managment/<int:pk>", views.managmentDetail.as_view()),
    path("patients/", views.patientList.as_view()),
    path("patient/<int:pk>", views.patientDetail.as_view()),
    path('refounds/', views.RefoundListCreateAPIView.as_view(), name='refound-list-create'),
    path('receptions/', views.ReceptionListCreateAPIView.as_view(), name='reception-list-create'),
    path('doctor/<int:doctor_id>/reservations/', views.DoctorReservationAPIView.as_view(), name='doctor-reservations'),
    path('specialties/', views.SpecialtyList.as_view(), name='specialty-list'),
    path('specialties/<int:specialty_id>/doctors/', views.DoctorsBySpecialty.as_view(), name='doctors-by-specialty'),
    path('doctor/<int:doctor_id>/reservations/', views.DoctorReservationAPIView.as_view(), name='doctor-reservations'),
    path('register/step2/', views.RegisterStepTwoAPIView.as_view(), name='register-step2'),  
    path('doctors/search/', views.DoctorSearchAPIView.as_view(), name='doctor-search')
]


{
    "username": "doctor2",
    "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMjg4NjIyMiwiaWF0IjoxNzEyNzk5ODIyLCJqdGkiOiI2ZTllZjllODU1Mzk0YmMxYmZhMDBmOWM0OTRhYzJkNSIsInVzZXJfaWQiOjR9.qS5Op1LVEO3YbtMZSiwF10mWk-kYyFlUMe_v-8n8Uc4",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEyNzk5ODgyLCJpYXQiOjE3MTI3OTk4MjIsImp0aSI6ImJjNmIwNmQ0OWI0MDQ5ODE4ZmFjZWUwNDk2ODBkZjdhIiwidXNlcl9pZCI6NH0.sRp7LwyFBbhptqOq-hckWD4yBuc9dDRAEiB0dAOacBY"
    }
}