# ─── views.py  (imports) ──────────────────────────────────────────────────────
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction  

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

from openai import OpenAI
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, json
from datetime import datetime

from .models import (
    Profile, UserProfile, FamilyMember,
    JournalEntry, Doctor
)
from .forms import (
    DoctorSignupForm, UserProfileForm, FamilyMemberForm
)
def signup_choice(request):
    """
    Shows the “Patient or Doctor?” choice screen.
    """
    return render(request, "signup_choice.html")
# ─── Doctor sign-up (public — NO login_required) ─────────────────────────────
def doctor_signup(request):
    """
    Create a new Doctor account + linked Django User in one atomic step.
    Username == doctor_id so the doctor logs in with that ID.
    """
    if request.method == "POST":
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # split out the extra password field
                pwd        = form.cleaned_data.pop('password')
                doctor_id  = form.cleaned_data["doctor_id"]
                email      = form.cleaned_data["email"]

                # 1) create auth user
                user = User.objects.create_user(
                    username=doctor_id,
                    email=email,
                    password=pwd
                )

                # 2) create Doctor profile
                doctor           = form.save(commit=False)
                doctor.user      = user
                doctor.full_name = form.cleaned_data["full_name"]
                doctor.save()

            messages.success(request, "Doctor account created — please sign in.")
            return redirect("doctor_login")
    else:
        form = DoctorSignupForm()

    # ✅ FIXED TEMPLATE PATH
    return render(request, "doctor_signup.html", {"form": form})

# ... (all your other imports)
from django.contrib.auth.decorators import login_required

# ─── Doctor login ────────────────────────────────────────────────
def doctor_login(request):
    """
    Doctor sign-in via doctor_id + password.
    """
    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        password  = request.POST.get("password")

        user = authenticate(request, username=doctor_id, password=password)

        # user must exist *and* be linked to a Doctor profile
        if user and Doctor.objects.filter(user=user).exists():
            login(request, user)
            return redirect("doctor_dashboard")          # <── straight to dashboard
        messages.error(request, "Invalid Doctor ID or password.")

    return render(request, "doctor_login.html")


# ─── Doctor dashboard ────────────────────────────────────────────
@login_required(login_url="doctor_login")                # <── explicit!
def doctor_dashboard(request):
    doctor   = Doctor.objects.filter(user=request.user).first()
    patients = UserProfile.objects.filter(assigned_doctor=doctor) if doctor else []
    return render(request, "doctor_dashboard.html",
                  {"doctor": doctor, "patients": patients})


# Temporary storage for user tokens (use a database in production)
user_tokens = []

@login_required
def journal_view(request):
    if request.method == 'POST':
        user = request.user
        pain_level = request.POST.get('painLevel', 'No Pain 😃')
        energy_level = request.POST.get('energyLevel', 'Excellent – no fatigue 😃')
        shortness_of_breath = request.POST.get('breath', 'No, not at all')
        chest_pain = request.POST.get('chestPain', 'No Pain 😃')
        physical_activity = request.POST.get('physicalActivity', 'None')
        stress_level = request.POST.get('stressLevel', 'No stress 😃')
        swelling = request.POST.get('swelling', 'No swelling 🦶')
        emergency_symptoms = request.POST.get('emergency', 'No')
        extra_note = request.POST.get('extraNote', 'No additional notes provided.')

        # Define normalized mappings for a fixed range (0-10)
        normalized_mapping = {
            'painLevel': {
                "No Pain 😃": 0,
                "Very Mild Pain 🙂": 1,
                "Mild Pain 🙂": 2,
                "Discomfort 😐": 3,
                "Moderate Pain 😣": 4,
                "Uncomfortable 😖": 5,
                "Severe Pain 😢": 6,
                "Very Severe Pain 😭": 7,
                "Intense Pain 💀": 8,
                "Extreme Pain 💀💀": 9,
                "Worst Possible Pain 💀💀💀": 10
            },
            'energyLevel': {
                "Excellent – no fatigue 😃": 0,
                "Good – mild fatigue 🙂": 3,
                "Fair – moderate fatigue 😐": 6,
                "Poor – severe fatigue 😞": 10,
            },
            'breath': {
                "No, not at all": 0,
                "Yes, during mild activity": 3,
                "Yes, during strenuous activity": 6,
                "Yes, even at rest": 10
            },
            'chestPain': {
                "No Pain 😃": 0,
                "Mild discomfort 🙂": 3,
                "Moderate pain 😣": 6,
                "Severe pain 😖": 10
            },
            'physicalActivity': {
                "More than usual": 0,
                "As much as usual": 3,
                "Less than usual": 6,
                "None": 10
            },
            'stressLevel': {
                "No stress 😃": 0,
                "Mild stress 🙂": 3,
                "Moderate stress 😐": 6,
                "High stress 😖": 10
            },
            'swelling': {
                "No swelling 🦶": 0,
                "Mild swelling 🦶": 3,
                "Moderate swelling 🦶": 6,
                "Severe swelling 🦶": 10
            },
            'emergency': {
                "No": 0,
                "Mild, manageable at home": 3,
                "Moderate, resolved with rest": 6,
                "Severe, required attention": 10
            }
        }

        # Convert each response to its normalized numeric value
        pain_value = normalized_mapping['painLevel'].get(pain_level, 0)
        energy_value = normalized_mapping['energyLevel'].get(energy_level, 0)
        breath_value = normalized_mapping['breath'].get(shortness_of_breath, 0)
        chest_value = normalized_mapping['chestPain'].get(chest_pain, 0)
        physical_value = normalized_mapping['physicalActivity'].get(physical_activity, 0)
        stress_value = normalized_mapping['stressLevel'].get(stress_level, 0)
        swelling_value = normalized_mapping['swelling'].get(swelling, 0)
        emergency_value = normalized_mapping['emergency'].get(emergency_symptoms, 0)

        categories = [
            "Pain Level", "Energy Levels", "Shortness of Breath",
            "Chest Pain", "Physical Activity", "Stress Levels",
            "Swelling in Feet/Ankles", "Emergency Symptoms"
        ]
        values = [pain_value, energy_value, breath_value, chest_value,
                  physical_value, stress_value, swelling_value, emergency_value]

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        chart_path = os.path.join(BASE_DIR, f"health_tracker_{user.username}.png")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Plot the graph with a fixed x-axis range (0-10)
        plt.figure(figsize=(12, 7))
        plt.barh(categories, values, color='#37B897', edgecolor='black')
        plt.xlabel("Level/Severity (0-10)")
        plt.title(f"{user.username}'s Health Report - {timestamp}")
        plt.xlim(0, 10)  # Ensures a fixed range on the x-axis
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.savefig(chart_path)
        plt.close()

        # Prepare the email with the graph attached
        email_subject = f"📝 {user.username}'s Health Report - {timestamp}"
        email_message = f"""
        Hello {user.username},\n\nHere is your Daily Health Tracker submission:\n
        Pain Level: {pain_level}
        Energy Levels: {energy_level}
        Shortness of Breath: {shortness_of_breath}
        Chest Pain: {chest_pain}
        Physical Activity: {physical_activity}
        Stress Levels: {stress_level}
        Swelling in Feet/Ankles: {swelling}
        Emergency Symptoms: {emergency_symptoms}
        Additional Notes: {extra_note}
        
        📝 Attached is your health report graph.
        """

        email = EmailMessage(email_subject, email_message, 'ngp.cura@gmail.com', ['ngp.cura@gmail.com'])
        email.attach_file(chart_path)
        email.send()
        os.remove(chart_path)

        return redirect('journal_confirmation')

    return render(request, 'journal.html')

@login_required
def add_profile(request):
    if request.method == "POST":
        print("Received POST Data:", request.POST)  # Debugging print

        # Retrieve and validate age
        try:
            age_value = int(request.POST.get('age', 0))
        except ValueError:
            return render(request, 'addprofile.html', {'error': 'Invalid age format.'})

        # Ensure the user has a UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'name': request.POST.get('name', ''), 'age': age_value}
        )

        # Update all fields explicitly
        profile.name = request.POST.get('name', '')
        profile.age = age_value
        profile.gender = request.POST.get('gender', '')
        profile.dob = request.POST.get('dob', None)
        profile.phone = request.POST.get('phone', '')
        profile.email = request.POST.get('email', '')
        profile.location = request.POST.get('location', '')
        profile.emergency_contact = request.POST.get('emergency', '')

        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']

        profile.save()

        # ✅ Handle multiple family members
        family_names = request.POST.getlist('family_name[]')
        relationships = request.POST.getlist('relationship[]')
        family_ages = request.POST.getlist('family_age[]')
        family_genders = request.POST.getlist('family_gender[]')
        family_locations = request.POST.getlist('family_location[]')
        family_photos = request.FILES.getlist('family_photo[]')

        for i in range(len(family_names)):
            if family_names[i].strip() == "":
                continue  # Skip empty family members

            try:
                family_age = int(family_ages[i])
            except ValueError:
                family_age = 0  # Default to 0 if invalid

            family_member = FamilyMember(
                user=request.user,
                name=family_names[i],
                relationship=relationships[i],
                age=family_age,
                gender=family_genders[i],
                location=family_locations[i],
            )

            if i < len(family_photos):  # Attach photo if available
                family_member.photo = family_photos[i]

            family_member.save()

        return redirect('famil')

    return render(request, 'addprofile.html')

@login_required
def family_view(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    family_members = FamilyMember.objects.filter(user=request.user)
    
    return render(request, 'famil.html', {'profile': profile, 'family_members': family_members})

# ✅ User Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Choose another one.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        
        # ✅ Remove this: Profile.objects.create(user=user, is_new=True)
        # The Profile is automatically created by signals.py

        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'signup.html')


# ✅ User Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Check if the user is new
            user_profile = Profile.objects.get(user=user)
            if user_profile.is_new:
                user_profile.is_new = False  # ✅ Fix: Mark user as not new
                user_profile.save()
                return redirect('tour')  # ✅ First-time users still get tour

            return redirect('famil')  # ✅ Existing users go to home

        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')

# ✅ User Logout View
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login after logout

# ✅ Protected Home View (Only Logged-in Users Can Access)

@login_required(login_url='login')
def home(request, user_id=None):
    # Load the logged-in user's profile (existing logic)
    user_profile = Profile.objects.get(user=request.user)

    # Redirect first-time users to the tour page (existing logic)
    if user_profile.is_new:
        user_profile.is_new = False
        user_profile.save()
        return redirect('tour')

    # New feature: Load a selected family member's home page if user_id is provided
    if user_id:
        selected_user_profile = FamilyMember.objects.filter(id=user_id, user=request.user).first()
        if not selected_user_profile:
            messages.error(request, "User profile not found.")
            return redirect('famil')
    else:
        # Default to the logged-in user's profile
        selected_user_profile = UserProfile.objects.filter(user=request.user).first()

    return render(request, 'home.html', {'user_profile': selected_user_profile})

# ✅ Protected Views
@login_required(login_url='login')
def famil(request):
    return render(request, 'famil.html')

@login_required(login_url='login')
def appointments(request):
    return render(request, 'appointments.html')

@login_required(login_url='login')
def journal(request):
    return render(request, 'jour.html')

@login_required(login_url='login')
def activity(request):
    return render(request, 'activity.html')

@login_required(login_url='login')
def settingscroll(request):
    return render(request, 'settingscroll.html')

@login_required(login_url='login')
def leaderboard(request):
    return render(request, 'leaderboard.html')

@login_required(login_url='login')
def noactivity(request):
    return render(request, 'noactivity.html')

@login_required(login_url='login')
def notifications(request):
    return render(request, 'notifications.html')

@login_required(login_url='login')
def settings(request):
    return render(request, 'settings.html')

@login_required(login_url='login')
def rewards(request):
    return render(request, 'rewards.html')

@login_required(login_url='login')
def symptom(request):
    return render(request, 'symptom.html')

@login_required(login_url='login')
def nomedical(request):
    return render(request, 'nomedical.html')

@login_required(login_url='login')
def med_aspirin(request):
    return render(request, 'med_aspirin.html')

@login_required(login_url='login')
def med_capsule(request):
    return render(request, 'med_capsule.html')

@login_required(login_url='login')
def med_pill(request):
    return render(request, 'med_pill.html')

@login_required(login_url='login')
def med_schedule(request):
    return render(request, 'med_schedule.html')

@login_required(login_url='login')
def medications(request):
    return render(request, 'medications.html')

# ✅ Tour Page (Only for First-Time Users)
@login_required(login_url='login')
def tour(request):
    return render(request, 'tour.html')


# ✅ 🔥 Save Firebase Device Token (For Push Notifications)
@csrf_exempt
def save_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")

            if token and token not in user_tokens:
                user_tokens.append(token)
                print(f"✅ New Firebase Token Saved: {token}")

            return JsonResponse({"success": True, "tokens": user_tokens})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@csrf_exempt
def chatbot_query(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("message", "")

        # Load FAISS DB and search for relevant chunks
        db = FAISS.load_local("happ/embeddings/faiss_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        docs = db.similarity_search(query, k=3)

        # ✅ Fallback if nothing relevant is found
        if not docs:
            return JsonResponse({"answer": "I couldn’t find anything relevant in my knowledge base. Please try rephrasing your question."})
        
        context = "\n\n".join([doc.page_content for doc in docs])

        # Send query and context to OpenAI
        # ✅ NEW API format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful medical assistant. Only answer based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}"
                }
            ]
        )

        

        # ✅ Extract answer from response
        answer = response.choices[0].message.content

         # ✅ Log query and response
        print(f"[CHATBOT QUERY] User: {query}")
        print(f"[CHATBOT RESPONSE] Bot: {answer}")

        return JsonResponse({"answer": answer})