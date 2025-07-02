from django import forms
from .models import UserProfile, FamilyMember, Doctor
from django.contrib.auth.models import User

class DoctorSignupForm(forms.ModelForm):
    doctor_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=6,
        label="Password"
    )

    class Meta:
        model = Doctor
        fields = [
            'doctor_doctor_id',
            'doctor_full_name',
            'doctor_email',
            'doctor_speciality',
            'doctor_phone',
        ]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'gender', 'dob', 'phone', 'email', 'location', 'emergency_contact', 'photo', 'unique_id']

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relationship', 'age', 'gender', 'location', 'photo']
