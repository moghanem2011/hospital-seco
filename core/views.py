from django.conf import settings
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from .models import  Doctor, MedicalRecord, Medication, Payment, PaymentCheque, Prescription, Room, RoomBooking, Specialty, TimeSlot, generate_time_slots, managment, Patient, Pharmacy, Refound, Reception,Pharmacist
import uuid
from django.db.models import Count, Q
import json
import requests
from django.utils import timezone
from django.db.models import Q
from .serializers import (
    
    MedicalRecordSerializer,
    MedicationSerializer,
    PaymentChequeSerializer,
    PaymentSerializer,
    PrescriptionSerializer,
    RoomBookingSerializer,
    RoomSerializer,
    SpecialtySerializer,
    TimeSlotSerializer,
    doctorSerializer,
    managmentSerializer,
    PatientSerializer,
    PatientProfileSerializer,
    PharmacySerializer,
    ReceptionSerializer,
    RefoundSerializer,
    PharmacistSerializer,
   
)
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework import generics,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from user_auth.permissions import (
    DoctorPermission,
    ReciptionPermission,
    PharmacyPermission
)


class MedicationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

class MedicationListAPIView(generics.ListAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    
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
def get_time_slots_for_doctor1(request, doctor_id, day):
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
def Patientlist_for_doctor(request, doctor_id, day):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Fetch all time slots for the specified day and doctor
    time_slots = TimeSlot.objects.filter(doctor=doctor, day=day , is_booked=True)

    # Serialize the time slots
    serialized_time_slots = TimeSlotSerializer(time_slots, many=True)
    
    # Construct the response
    return Response({
        "doctor_id": doctor_id,
        "day": day,
         "time_slots": serialized_time_slots.data   
            })

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

    

class PharmacyView(APIView):
    def get(self, request, patient_id):
        medical_records = MedicalRecord.objects.filter(patient_id=patient_id)
        # Set the context to filter filled prescriptions
        context = {'filter_filled': True}
        serializer = MedicalRecordSerializer(medical_records, many=True, context=context)
        data = [record for record in serializer.data if record is not None]  # Filter out None records
        return Response(data)


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
    
class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                doctor = Doctor.objects.get(user=user)
                return Response({
                    "message": "Login successful.",
                    "doctor_id": doctor.id
                }, status=status.HTTP_200_OK)
            except Doctor.DoesNotExist:
                return Response({
                    "message": "Doctor profile not found."
                }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "message": "Invalid credentials, please try again."
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginPHAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                pharmacist = Pharmacist.objects.get(user=user)
                return Response({
                    "message": "Login successful.",
                    "pharmacist_id": pharmacist.id
                }, status=status.HTTP_200_OK)
            except Doctor.DoesNotExist:
                return Response({
                    "message": "Pharmacist profile not found."
                }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "message": "Invalid credentials, please try again."
        }, status=status.HTTP_400_BAD_REQUEST)

class MedicalRecordView(APIView):
    def post(self, request):
        serializer = MedicalRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicalRecordDetailView(generics.RetrieveAPIView):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    lookup_field = 'id'

class PatientMedicalRecordsView(generics.ListAPIView):
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        """
        This view should return a list of all the medical records
        for the currently authenticated patient.
        """
        patient_id = self.kwargs['patient_id']
        return MedicalRecord.objects.filter(patient__id=patient_id)
    

class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}
    
class RoomBookingsViewSet(ModelViewSet):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        room = serializer.validated_data['room']
        serializer.validated_data['check_in_date'] = timezone.now().date()
        check_in_date = serializer.validated_data['check_in_date']
        try:
            check_out_date = serializer.validated_data['check_out_date']
        except KeyError:
            check_out_date = None
        
        # Check room availability
        if not self.is_room_available(room, check_in_date, check_out_date):
            return Response({"error": "Room is not available or not available for the selected dates."}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def is_room_available(self, room, check_in_date, check_out_date):
        if not room.available:
            return False
        
        null_checkouts = RoomBooking.objects.filter(check_out_date__isnull=True)
        not_null_checkouts = RoomBooking.objects.filter(check_out_date__isnull=False)
       
        null_checkout_overlapping_bookings = null_checkouts.filter(
                Q(room=room) &
                Q(status__in=['booked', 'checked_in'])
            ).count()
        
        if check_out_date is not None:
            non_nullable_overlapping_bookings = not_null_checkouts.filter(
                    Q(check_out_date__gt=check_in_date) &
                    Q(check_in_date__lt=check_out_date),
                    room=room,
                    status__in=['booked', 'checked_in']
                ).count()
        else:
                non_nullable_overlapping_bookings = not_null_checkouts.filter(
                    Q(check_out_date__gt=check_in_date),
                    room=room,
                    status__in=['booked', 'checked_in']
                ).count()
        return (null_checkout_overlapping_bookings + non_nullable_overlapping_bookings) < room.room_capacity

class PaymentChequeViewSet(ModelViewSet):
    queryset = PaymentCheque.objects.all()
    serializer_class = PaymentChequeSerializer
    lookup_field = 'pk'
    
    def get_paypal_token(self, request):
        token_url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {'grant_type': 'client_credentials'}
        auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET)
        response = requests.post(token_url, headers=headers, data=data, auth=auth)
        response.raise_for_status()
        return response.json()['access_token']
    
    @action(detail=True, methods=['GET'])
    def paynow(self, request, *args, **kwargs):
        paypal_token = self.get_paypal_token(request)
        paycheque = self.get_object()
        success_url = f"http://{request.get_host()}/api/paymentcheques/state/?status=successful&paycheque_id={paycheque.id}"
        failed_url = f"http://{request.get_host()}/api/paymentcheques/state/?status=failed&paycheque_id={paycheque.id}"
        
        data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": str(uuid.uuid4()),
                "amount": {
                    "currency_code": "USD",
                    "value": paycheque.amount_to_be_paid
                },
            }],
            "application_context": {
                "shipping_preference": "NO_SHIPPING",
                "return_url": success_url,
                "cancel_url": failed_url
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {paypal_token}',
        }
        
        response = requests.post('https://api.sandbox.paypal.com/v2/checkout/orders', headers=headers, data=json.dumps(data))
        if response.status_code == 201:
            payment = response.json()
            # Extract approval URL
            approval_url = next(link['href'] for link in payment['links'] if link['rel'] == 'approve')
            
            # Redirect the client to PayPal approval URL
            # In a web application, you would return a redirect response to the client
            # For example, in Django:
            return Response({"payment_url": approval_url}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something isn't right."}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['GET'])
    def state(self, request):
        token = request.GET.get('token')
        payer_id = request.GET.get('PayerID')

        if not token or (not payer_id and request.query_params.get('status') != "failed"):
            return Response({'error': 'Missing token or PayerID'}, status=400)

        access_token = self.get_paypal_token(request)  # Implement this function to obtain access token
        
        capture_url = f'https://api.sandbox.paypal.com/v2/checkout/orders/{token}/capture'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.post(capture_url, headers=headers)
        response_data = response.json()  # Extract JSON data from the response

        if response.status_code == 201:
            payment_info = {
                'payment_id': response_data.get('id'),
                'status': response_data.get('status'),
                'payer_name': f"{response_data['payer']['name']['given_name']} {response_data['payer']['name']['surname']}",
                'payer_email': response_data['payer']['email_address'],
                'amount': response_data['purchase_units'][0]['payments']['captures'][0]['amount']['value'],
                'currency': response_data['purchase_units'][0]['payments']['captures'][0]['amount']['currency_code'],
                'transaction_id': response_data['purchase_units'][0]['payments']['captures'][0]['id'],
                'payment_time': response_data['purchase_units'][0]['payments']['captures'][0]['create_time'][:10],
                # 'links': response_data['purchase_units'][0]['payments']['captures'][0]['links']
            }

            if request.query_params.get('status') == 'successful':
                paycheque_id = request.query_params.get('paycheque_id')
                if paycheque_id:
                    try:
                        paycheque = PaymentCheque.objects.get(pk=paycheque_id)
                        paycheque.status = "COMPLETED"  # Assuming "A" means Approved
                        paycheque.save()
                        
                        payment_info['paycheque'] = paycheque
                        payment = Payment.objects.create(**payment_info)
                        
                        serializer = PaymentSerializer(payment)  # No need to use 'data=' here
                        
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    
                    except PaymentCheque.DoesNotExist:
                        return Response({'error': 'PaymentCheque not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Handle other status codes and errors
                return Response({"message": response_data}, status=response.status_code)


class PaymentViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
        
                 
class UnfilledMedicalRecordsView(APIView):
    def get(self, request, patient_id):
        # Get all medical records for the specified patient
        medical_records = MedicalRecord.objects.filter(patient_id=patient_id)

        # Filter those medical records that only have unfilled prescriptions
        unfilled_medical_records = medical_records.annotate(
            filled_prescription_count=Count('prescriptions', filter=Q(prescriptions__is_filled=True)),
            total_prescription_count=Count('prescriptions')
        ).filter(filled_prescription_count=0, total_prescription_count__gt=0).distinct()

        # Serialize the medical record data
        serializer = MedicalRecordSerializer(unfilled_medical_records, many=True)
        return Response(serializer.data)
    
    def get(self, request, patient_id):
        medical_records = MedicalRecord.objects.filter(patient_id=patient_id)
        serializer = MedicalRecordSerializer(medical_records, many=True)
        return Response(serializer.data)

                        return Response({'error': 'PaymentCheque not found'}, status=404)
            return Response(payment_info, status=201)
        else:
            # Handle other status codes and errors
            return Response({"message": response_data}, status=response.status_code)
        
class FillPrescriptionView(APIView):
    def patch(self, request, pk):
        try:
            prescription = Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            return Response({'error': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)

        prescription.is_filled = True
        prescription.save()

        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class PatientsWithUnfilledPrescriptionsView(APIView):
    def get(self, request):
        # Find all medical records that are linked to at least one unfilled prescription
        medical_records_with_unfilled = MedicalRecord.objects.filter(
            prescriptions__is_filled=False
        ).distinct()
        
        # Extract patients from these medical records
        patients = {record.patient for record in medical_records_with_unfilled}
        
        # Serialize the patient data
        serializer = PatientSerializer(list(patients), many=True)
        return Response(serializer.data)
    
class MedicationSearchView(APIView):
    def get(self, request):
        # Get the query from request query parameters
        query = request.query_params.get('query', None)

        # Filter medications based on the query
        if query is not None:
            medications = Medication.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        else:
            medications = Medication.objects.all()

        # Serialize the medication data
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data)
