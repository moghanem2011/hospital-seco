from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
from datetime import timedelta

from project import settings
#from user_auth.serializers import username

class managment(models.Model):  
    name = models.CharField(max_length=100)


class Patient(models.Model):
    GENDER_TABLE =(
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    BLOOD_TABLE=(
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='patient_images/',null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER_TABLE)
    blood = models.CharField(max_length=3, choices=BLOOD_TABLE)
    patient_status = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Pharmacy(models.Model):  
    contact_number = models.CharField(max_length=15)
    location= models.CharField(max_length=20)
    name= models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} {self.location}"
    
    
class Pharmacist(models.Model):  
    contact_number = models.CharField(max_length=15)
    name= models.CharField(max_length=20)
    pharmacyID = models.ForeignKey(Pharmacy, on_delete=models.CASCADE,default=1)
    def __str__(self):
        return f"{self.name} {self.location}"

class Specialty(models.Model):
    title = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.title
    
class Doctor(models.Model):  
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    address = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='doctor_photos/', null=True, blank=True)
    doctor_price= models.CharField(max_length=15)
    university= models.CharField(max_length=30)
    specialty= models.ForeignKey(Specialty, related_name='doctors' , on_delete=models.CASCADE)
    pharmacyID = models.ForeignKey(Pharmacy, on_delete=models.CASCADE,default=1)


class Refound(models.Model):
    refound_amount=models.DecimalField(max_digits=10, decimal_places=10)


class Reception(models.Model):  
    name= models.CharField(max_length=20)
    refound_id=models.ForeignKey(Refound,on_delete=models.CASCADE)


class Reservation(models.Model):
    date = models.CharField(max_length=15)
    time_slot = models.TimeField()  # Time of the reservation
    payment_method = models.CharField(max_length=20)
    payment_amount = models.CharField(max_length=20)
    patientID = models.ForeignKey('Patient', on_delete=models.CASCADE, default=1)
    doctorID = models.ForeignKey('Doctor', on_delete=models.CASCADE, default=1)
    refund_id = models.ForeignKey('Refound', on_delete=models.CASCADE)  

    def __str__(self):
        return f"{self.date} {self.time_slot} {self.payment_method}"

    @classmethod
    def check_availability(cls, date, time_slot, doctor_id):
        count_reservations = cls.objects.filter(date=date, doctorID=doctor_id).count()
        if count_reservations >= 30:
            return False 
        existing_reservation = cls.objects.filter(date=date, time_slot=time_slot, doctorID=doctor_id).exists()
        if existing_reservation:
            return False
        return True

    @classmethod
    def remaining_reservations(cls, date, doctor_id):
        count_reservations = cls.objects.filter(date=date, doctorID=doctor_id).count()
        return 30 - count_reservations

    @classmethod
    def estimated_time_remaining(cls, date, time_slot, doctor_id):
        remaining_slots = cls.remaining_reservations(date, doctor_id)
        current_time = cls.objects.filter(date=date, time_slot__lte=time_slot, doctorID=doctor_id).count()
        estimated_time = (remaining_slots - current_time) * 15  # Assuming each slot is 15 minutes
        return timedelta(minutes=estimated_time)

    def save(self, *args, **kwargs):
        if not self.check_availability(self.date, self.time_slot, self.doctorID_id):
            raise ValidationError("This time slot is either full or already booked.")
        super().save(*args, **kwargs)



