from queue import Full
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import JSONField
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from project import settings
from user_auth.models import HospitalUser
from django.db import transaction

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
    user = models.OneToOneField(HospitalUser, on_delete=models.CASCADE, related_name='Pharmacist_profile', null=True)
    contact_number = models.CharField(max_length=15)
    name= models.CharField(max_length=20)
    pharmacyID = models.ForeignKey(Pharmacy, on_delete=models.CASCADE,default=1)
    def __str__(self):
        return f"{self.name}"

class Specialty(models.Model):
    title = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='specialty_photos/', null=True, blank=True)

    def __str__(self) -> str:
        return self.title
    
class Doctor(models.Model):  
    user = models.OneToOneField(HospitalUser, on_delete=models.CASCADE, related_name='doctor_profile', null=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    address = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='doctor_photos/', null=True, blank=True)
    doctor_price= models.CharField(max_length=15)
    university= models.CharField(max_length=30)
    specialty= models.ForeignKey(Specialty, related_name='doctors' , on_delete=models.CASCADE)
    pharmacyID = models.ForeignKey(Pharmacy, on_delete=models.CASCADE,default=1),
    


class Refound(models.Model):
    refound_amount=models.DecimalField(max_digits=10, decimal_places=10)


class Reception(models.Model):  
    name= models.CharField(max_length=20)
    refound_id=models.ForeignKey(Refound,on_delete=models.CASCADE)


class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=5)  # Format: 'HH:MM'
    end_time = models.CharField(max_length=5)    # Format: 'HH:MM'
    DAY_OF_WEEK = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
    day = models.CharField(max_length=9, choices=DAY_OF_WEEK)
    is_booked = models.BooleanField(default=False)
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.day} {self.start_time} - {self.end_time}"



def generate_time_slots(doctor, start_datetime, end_datetime, slot_duration, buffer_duration):
    time_slots = []

    # Convert start_datetime and end_datetime to datetime objects
    start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
    end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')

    current_time = start_datetime
    slot_duration = timedelta(minutes=slot_duration)
    buffer_duration = timedelta(minutes=buffer_duration)

    while current_time < end_datetime:
        slot_start = current_time
        slot_end = current_time + slot_duration
        
        # Convert slot_start and slot_end to strings in the desired format 'HH:MM:SS'
        slot_start_str = slot_start.strftime('%H:%M:%S')  # Changed format
        slot_end_str = slot_end.strftime('%H:%M:%S')      # Changed format
        day_of_week = slot_start.strftime('%A')  # Extract the day of the week

        # Create a TimeSlot object and save it to the database
        time_slot = TimeSlot(
            start_time=slot_start_str,
            end_time=slot_end_str,
            day=day_of_week,  # Assume the TimeSlot model has a 'day' field
            doctor=doctor
        )
        time_slot.save()

        # Append the time slot object to the list of time slots
        time_slots.append(time_slot)

        # Move to the next slot accounting for slot duration
        current_time += slot_duration

        # Add buffer duration to current time
        current_time += buffer_duration

    return time_slots

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE , null=True)
    date = models.DateField(auto_now_add=True)
    record_name = models.CharField(max_length=255, editable=False, blank=True)

    def save(self, *args, **kwargs):
        # Set the record_name only if it's a new record and not already set
        if not self.id and not self.record_name:
            self.record_name = f"The Record written by {self.doctor.firstname} {self.doctor.lastname}"
        super(MedicalRecord, self).save(*args, **kwargs)

class Diagnosis(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, related_name='diagnoses', on_delete=models.CASCADE)
    description = models.TextField()

class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, related_name='prescriptions', on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    is_filled = models.BooleanField(default=False)

    
class Room(models.Model):
    """Room data model for registering available rooms.

    Args:
        models (room_type): this defines what kinda room we are creating or adding.
        models (available): we will need this later when patients are booking rooms.

    Returns:
        _room object_: _room object that will be migrated into the database on command_
    """
    
    _ROOM_TYPES = [
        ('general_ward', 'General Ward'),
        ('semi_private', 'Semi-Private Room'),
        ('private', 'Private Room'),
        ('deluxe', 'Deluxe Room'),
        ('icu', 'Intensive Care Unit (ICU) Room'),
        ('nicu', 'Neonatal Intensive Care Unit (NICU) Room'),
        ('maternity', 'Maternity Suite'),
        ('recovery', 'Recovery Room'),
        ('isolation', 'Isolation Room'),
    ]
    DEFAULT_ROOM_CAPACITY = 10
    MAXIMUM_ROOM_CAPACITY = 10
    
    room_type = models.CharField(
        max_length=20,
        choices=_ROOM_TYPES,
        default='general_ward',
    )
    available = models.BooleanField(default=True)
    room_capacity = models.PositiveBigIntegerField(validators=[MinValueValidator(1),
                                                               MaxValueValidator(MAXIMUM_ROOM_CAPACITY)],
                                                   default=DEFAULT_ROOM_CAPACITY, blank=True)

    def __str__(self):
        """for representing rooms in the admin model and the browsable API"""
        return f"{self.room_type} - {self.id}"
    
    
    
    
class RoomBooking(models.Model):
    """Booking data model for booking empty and available rooms."""
    BOOKING_STATUS = [
        ('booked', 'Booked'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]
    paycheque = models.OneToOneField('PaymentCheque', on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField(auto_now_add=True)
    check_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='booked',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.patient} in {self.room} from {self.check_in_date} to {self.check_out_date or 'N/A'}"

    # class Meta:
    #     unique_together = ('room', 'check_in_date', 'check_out_date')
        
    
    # def save(self, *args, **kwargs):
    #     with transaction.atomic():
    #         # Check for overlapping bookings that would exceed room capacity
    #         overlapping_bookings = RoomBooking.objects.filter(
    #             room=self.room,
    #             status__in=['booked', 'checked_in'],
    #             check_in_date__lt=self.check_out_date,
    #             check_out_date__gt=self.check_in_date,
    #         ).count()
            
    #         if overlapping_bookings >= self.room.room_capacity:
    #             raise ValueError("This room is already at full capacity for the selected dates.")
            
    #         super().save(*args, **kwargs)
    
    
class PaymentCheque(models.Model):
    DEFAULT_PAYMENT_STATUS = 'PENDING'
    PAYMENT_STATUS = [
        ('pending', 'PENDING'),
        ('declined', 'DECLINED'),
        ('completed', 'COMPLETED')
    ]
    amount_to_be_paid = models.CharField(max_length=100) # this is the total amount paid
    status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default=DEFAULT_PAYMENT_STATUS)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'PaymentChqeue is {self.status} and requested at {self.requested_at} for {self.roombooking or 'N/A'}.'
    
class Payment(models.Model):
    payment_id = models.CharField(max_length=255)
    paycheque = models.OneToOneField(PaymentCheque, on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=100, default="PayPal")
    status = models.CharField(max_length=255)
    payer_name = models.CharField(max_length=255)
    payer_email = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=255, default="USD")
    transaction_id = models.CharField(max_length=255)
    payment_time = models.DateField()
    
    def __str__(self):
        return f"Payment for paycheque {self.paycheque} by {self.payer_name} {self.payer_email}."
    

class Medication(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=255)
    form = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    description = models.TextField()
    side_effects = models.JSONField()  # Requires Django 3.1+
    quantity = models.IntegerField()
    availability = models.CharField(max_length=50)
    photo = models.URLField(max_length=200)

    def _str_(self):
        return self.name