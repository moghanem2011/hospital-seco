from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
import datetime
from rest_framework import serializers

from .models import (
    Doctor,
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




class RefoundSerializer(ModelSerializer):
    class Meta:
        model = Refound
        fields = '__all__'



class ReceptionSerializer(ModelSerializer):
    class Meta:
        model = Reception
        fields = '__all__'

