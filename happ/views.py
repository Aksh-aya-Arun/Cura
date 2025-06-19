from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile  # Profile model must have is_new field
from .models import UserProfile, FamilyMember
from django.core.mail import send_mail
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from django.core.mail import EmailMessage
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Profile, JournalEntry  # Import existing models
from django.http import JsonResponse


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
        
        from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def get_chatbot_response(user_message):
    user_message = user_message.lower()
    
    # Keyword-based response mapping
    response_mapping = [
        {"keywords": ["hokkaido baked cheese tart"], "response": "Hokkaido Baked Cheese Tarts are delicious, but they’re high in saturated fats and sugars, which can raise cholesterol and affect heart health. Since managing fat and sugar intake is crucial for your condition, it’s best to limit these treats. If you’re looking for a tasty alternative, how about trying the Soy Pudding from Mr. Bean? It’s smooth, naturally sweetened, and lower in saturated fats—making it a more heart-friendly choice. Let me know if you’d like more snack recommendations around Singapore!"},
        
        {"keywords": ["feeling good"], "response": "Good to hear!"},
        
        {"keywords": ["not good"], "response": "Any discomfort you feel?"},
        
        {"keywords": ["knee pain", "exercise alternative"], "response": "Hey! Sorry to hear you’re dealing with limb pain. That sounds uncomfortable. Since you’ve got coronary artery disease, it’s super important to choose exercises that are gentle on your body while still keeping your heart healthy. If your doctor, Dr. Lim, previously recommended the seated leg raise (10 reps, 3 sets), you could try swapping it for ankle pumps (15 reps per leg). They’re great for improving circulation without putting too much strain on your limbs. Another simple option is the heel-to-toe walk—do this for about 5 minutes. It helps with balance and leg strength but is still low-impact. If you’re feeling up to it, gentle stretches like calf stretches against the wall (hold for 20 seconds, repeat 3 times per leg) can also relieve tension. But here’s the deal—if the pain is new, severe, or comes with things like chest pain, swelling, or numbness, please stop immediately and seek medical help. Better safe than sorry! Let me know if you’d like some guided videos for these exercises or if you want me to check with your care team for more personalized recommendations. You’ve got this—take it slow and steady!"},
        
        {"keywords": ["drowsiness", "side effect"], "response": "Hey! I’m sorry you’re feeling drowsy—that can be tough. Yes, amlodipine can sometimes cause drowsiness because it helps to relax and widen your blood vessels, lowering your blood pressure. That drop in blood pressure can sometimes make you feel a bit sleepy or sluggish. But here’s the thing—if the drowsiness came on suddenly, is severe, or if you’re feeling chest pain, shortness of breath, fainting, or confusion, you need to get medical help immediately. Please don’t wait—call for emergency help right away. If it’s just a mild drowsy feeling, here are a few things you could try: Keep yourself hydrated—sometimes a glass of water helps perk you up! Try a light walk or some gentle stretching if you feel up to it; it can boost your energy. Skip heavy meals or alcohol right now, as they can sometimes make drowsiness worse. But, if this drowsiness is messing with your daily routine, don’t just push through it. Let your doctor know. Sometimes, they might adjust your dose or try a different medication, which may not make you as sleepy. If you’re still feeling concerned, we can raise this issue to your doctor and get their advice. Just let me know—I’m here to help!"},
        
        {"keywords": ["contact number", "postpone appointment"], "response": "Of course! You can reschedule your appointment at Ng Teng Fong Hospital by calling 6908 2222. They’ll be happy to help you find a new time that works for you. If you would like to top up your medication in the meantime until your next appointment date, I can assist you with placing an order. Let me know how I can help!"},
        
        {"keywords": [], "response": "I'm not sure about that. Can you ask me something else?"} # Default response
    ]
    
    # Find a matching response based on keywords
    for item in response_mapping:
        if any(keyword in user_message for keyword in item["keywords"]):
            return item["response"]
    
    return "I'm not sure about that. Can you ask me something else?"

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        response = get_chatbot_response(user_message)
        return JsonResponse({"response": response})