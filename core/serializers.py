from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer
import datetime
from rest_framework import serializers

from .models import (
    Diagnosis,
    Doctor,
    MedicalRecord,
    Prescription,
    Specialty,
    TimeSlot,
    managment,
    Patient,
    Pharmacy,
    Pharmacist,
    Refound,
    Reception,
    
)



class TimeSlotSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)  # Add this line

    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'day', 'is_booked', 'patient_name', 'patient_id']  # Include patient_id here

    def get_patient_name(self, obj):
        # This method returns the name of the patient if the slot is booked
        return obj.patient.firstname + " " + obj.patient.lastname if obj.patient else None

    
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['name', 'photo']

        photo = serializers.ImageField(use_url=True)

class SpecialtySerializer(ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'title','photo']

        
class doctorSerializer(serializers.ModelSerializer):
    
    specialty_name = serializers.CharField(source='specialty.title', read_only=True)
    class Meta:
        model = Doctor
        fields = ['id', 'firstname', 'lastname', 'age', 'address', 'photo', 'doctor_price', 'university','specialty_name', 'specialty']


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
        ) 


class managmentSerializer(ModelSerializer):
    class Meta:
        model = managment

 
class PatientSerializer(ModelSerializer):
    class Meta:
        model = Patient
        exclude = ["patient_status"]

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ["patient_status"]

    def create(self, validated_data):
        # Extract 'user' from 'validated_data' if it exists, defaulting to 'None' if it doesn't
        user = validated_data.pop('user', None)

        # If 'user' wasn't explicitly provided in 'validated_data', use the request user
        if user is None:
            user = self.context['request'].user

        patient_profile = Patient(user=user, **validated_data)
        patient_profile.save()
        return patient_profile

class PharmacySerializer(ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'

class PharmacistSerializer(ModelSerializer):
    class Meta:
        model = Pharmacist
        fields = '__all__'


class RefoundSerializer(ModelSerializer):
    class Meta:
        model = Refound
        fields = '__all__'



class ReceptionSerializer(ModelSerializer):
    class Meta:
        model = Reception
        fields = '__all__'

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = ['description']

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['medication_name', 'dosage']

class MedicalRecordSerializer(serializers.ModelSerializer):
    diagnoses = DiagnosisSerializer(many=True)
    prescriptions = PrescriptionSerializer(many=True)
    patient_id = serializers.IntegerField()
    doctor_id = serializers.IntegerField()  # Changed to doctor_id
    doctor_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = ['record_name','id', 'patient_id', 'doctor_id','doctor_name', 'date', 'diagnoses', 'prescriptions']
        read_only_fields = ['record_name']

    def get_doctor_name(self, obj):
        return f"{obj.doctor.firstname} {obj.doctor.lastname}" if obj.doctor else None


    def create(self, validated_data):
        # Extract nested data
        diagnoses_data = validated_data.pop('diagnoses', [])
        prescriptions_data = validated_data.pop('prescriptions', [])

        # Fetch the patient instance using patient_id
        patient_id = validated_data.pop('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)

        # Fetch the doctor instance using doctor_id
        doctor_id = validated_data.pop('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Create the MedicalRecord instance
        medical_record = MedicalRecord.objects.create(patient=patient, doctor=doctor, **validated_data)

        # Create Diagnosis instances
        for diagnosis_data in diagnoses_data:
            Diagnosis.objects.create(medical_record=medical_record, **diagnosis_data)

        # Create Prescription instances
        for prescription_data in prescriptions_data:
            Prescription.objects.create(medical_record=medical_record, **prescription_data)

        medical_record.save()  # Explicitly call save to ensure the custom logic is executed
        return medical_record