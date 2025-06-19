from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True)  # Default to new user

    def __str__(self):
        return self.user.username

class JournalEntry(models.Model):
    date = models.CharField(max_length=50)
    details = models.TextField()

    def _str_(self):
        return self.date
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    location = models.CharField(max_length=200)
    emergency_contact = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.name

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="family_members")
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    location = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(upload_to='family_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"