from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import  Doctor, Specialty, TimeSlot, generate_time_slots, managment, Patient, Pharmacy, Refound, Reception
from .serializers import (
    
    SpecialtySerializer,
    TimeSlotSerializer,
    doctorSerializer,
    managmentSerializer,
    PatientSerializer,
    PatientProfileSerializer,
    PharmacySerializer,
    ReceptionSerializer,
    RefoundSerializer,
   
)
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from datetime import datetime
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from user_auth.permissions import (
    DoctorPermission,
    ReciptionPermission,
    PharmacyPermission
)


@api_view(['POST'])
def generate_time_slots_api(request):
    doctor_id = request.data.get('doctor_id')
    start_datetime_str = request.data.get('start_datetime_str')
    end_datetime_str = request.data.get('end_datetime_str')
    slot_duration = request.data.get('slot_duration')
    buffer_duration = request.data.get('buffer_duration')

    if not start_datetime_str or not end_datetime_str:
        return Response({"error": "Start datetime or end datetime is missing."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor with the provided ID does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Extract hour part from start and end datetimes
    start_hour = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S').strftime('%H')
    end_hour = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S').strftime('%H')

    # Convert hour part to desired format (e.g., "23 FEB")
    start_hour_str = datetime.strptime(start_hour, '%H').strftime('%d %b')
    end_hour_str = datetime.strptime(end_hour, '%H').strftime('%d %b')

    # Combine start and end hour strings
    hour_range = f"{start_hour_str} - {end_hour_str}"

    # Generate time slots
    time_slots = generate_time_slots(doctor=doctor, start_datetime=start_datetime_str, end_datetime=end_datetime_str, slot_duration=slot_duration, buffer_duration=buffer_duration)

    # Serialize time slots into dictionaries
    serialized_time_slots = TimeSlotSerializer(time_slots, many=True).data

    # Optionally, you can serialize and return the time slots along with hour range as a response
    response_data = {
        'hour_range': hour_range,
        'time_slots': serialized_time_slots
    }
    return Response(response_data)

@api_view(['GET'])
def get_time_slots_for_doctor(request, doctor_id, day):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    # Fetch available time slots for the specified day and doctor
    # Ensure only unbooked slots are fetched
    time_slots = TimeSlot.objects.filter(doctor=doctor, day=day, is_booked=False)

    # Serialize the time slots
    serialized_time_slots = TimeSlotSerializer(time_slots, many=True).data

    # Construct the response
    response_data = {
        "DAY": day,
        "time_slots": serialized_time_slots
    }

    return Response(response_data)
    
@api_view(['POST'])
def book_appointment(request):
    slot_id = request.data.get('slot_id')
    patient_id = request.data.get('patient_id')
    
    if not slot_id or not patient_id:
        return Response({"error": "Slot ID and Patient ID are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        slot = TimeSlot.objects.get(id=slot_id)
        if slot.is_booked:
            return Response({"error": "This time slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
        
        patient = Patient.objects.get(id=patient_id)
        slot.patient = patient
        slot.is_booked = True
        slot.save()
        booked_time = slot.start_time
        day = slot.day
        return Response({"success": "Appointment booked successfully.", "slot_id": slot_id, "day": day, "start_time": booked_time})

    except TimeSlot.DoesNotExist:
        return Response({"error": "Time slot not found."}, status=status.HTTP_404_NOT_FOUND)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_patients_for_doctor(request, doctor_id):
    try:
        # Get all booked time slots for the specific doctor
        time_slots = TimeSlot.objects.filter(doctor_id=doctor_id, is_booked=True)
    except TimeSlot.DoesNotExist:
        return Response({"error": "No appointments found for this doctor."}, status=status.HTTP_404_NOT_FOUND)

    # Extract the patient data from the time slots
    patients = {slot.patient for slot in time_slots if slot.patient is not None}
    
    # Serialize the patient data
    serialized_patients = PatientSerializer(list(patients), many=True).data

    return Response(serialized_patients)

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
    
