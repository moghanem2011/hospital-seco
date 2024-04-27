from django.contrib.auth import password_validation
from rest_framework import serializers
from .models import HospitalUser

class HospitalUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[password_validation.validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = HospitalUser
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        user = HospitalUser(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

#class PatientProfileSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = PatientProfile
#        fields = ('condition', 'age')

#    def create(self, validated_data):
#        user = self.context['request'].user
#        patient_profile = PatientProfile(
#            user=user,
            
#        )
#        patient_profile.save()
#        return patient_profile
