from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Doctor, Specialty, managment, Patient, Pharmacy, Refound, Reception,Reservation
from .serializers import (
    SpecialtySerializer,
    doctorSerializer,
    managmentSerializer,
    PatientSerializer,
    PatientProfileSerializer,
    PharmacySerializer,
    ReceptionSerializer,
    RefoundSerializer,
    ReservationSerializer
)

from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from user_auth.permissions import (
    DoctorPermission,
    ReciptionPermission,
    PharmacyPermission
)



class DoctorSearchAPIView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = doctorSerializer

    def get_queryset(self):
        print(self.request.query_params)
        queryset = super().get_queryset()
        firstname = self.request.query_params.get('firstname', None)
        lastname = self.request.query_params.get('lastname', None)
        specialty_id = self.request.query_params.get('specialty_id')
        print(f"Searching for: firstname={firstname}, lastname={lastname}")  # Debug print

        if specialty_id:
            queryset = queryset.filter(specialty_id=specialty_id)

        if firstname:
            queryset = queryset.filter(firstname__icontains=firstname)
            
        if lastname:
            queryset = queryset.filter(lastname__icontains=lastname)

        return queryset

    

    

class DoctorReservationAPIView(generics.ListAPIView):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Reservation.objects.filter(doctorID_id=doctor_id)
        
class DoctorList(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = doctorSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsAdminUser | ReciptionPermission]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class DoctorDetail(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):  # Added generics.CreateAPIView
    queryset = Doctor.objects.all()
    serializer_class = doctorSerializer
    permission_classes = [IsAdminUser | ReciptionPermission]



class ManagmentList(generics.ListCreateAPIView):
    queryset = managment.objects.all()
    serializer_class = managmentSerializer
    permission_classes = [IsAdminUser]


class patientList(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    
    

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsAdminUser | ReciptionPermission]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
        
class patientDetail(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
     queryset = Patient.objects.all()
     serializer_class = PatientSerializer
     permission_classes = [IsAdminUser | ReciptionPermission]


class RegisterStepTwoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PatientProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Profile created successfully."}, status=201)
        return Response(serializer.errors, status=400)


class pharmacyList(generics.ListCreateAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    def get(self, request):
        user = request.user
        if user.role != 2:
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            pharamcy = pharamcy.objects.all()
            serializer = self.serializer_class(pharamcy, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)
        



class RefoundListCreateAPIView(APIView):
    
    def get(self, request):
        refounds = Refound.objects.all()
        serializer = RefoundSerializer(refounds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RefoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReceptionListCreateAPIView(APIView):
    def get(self, request):
        receptions = Reception.objects.all()
        serializer = ReceptionSerializer(receptions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReceptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SpecialtyList(generics.ListAPIView):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer

class DoctorsBySpecialty(generics.ListAPIView):
    serializer_class = doctorSerializer

    def get_queryset(self):
        specialty_id = self.kwargs['specialty_id']
        return Doctor.objects.filter(specialty__id=specialty_id)
    
class DoctorReservationAPIView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Reservation.objects.filter(doctorID_id=doctor_id).order_by('time_slot')

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Check for time slot availability
            doctor_id = request.data.get('doctorID')
            time_slot = request.data.get('time_slot')
            if Reservation.objects.filter(doctorID_id=doctor_id, time_slot=time_slot).exists():
                return Response({"error": "Time slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)