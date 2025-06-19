from django import forms
from .models import UserProfile, FamilyMember

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'gender', 'dob', 'phone', 'email', 'location', 'emergency_contact', 'photo']

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relationship', 'age', 'gender', 'location', 'insurance', 'notes', 'photo']
