from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
import os
from django.shortcuts import render
from .views import chatbot_response
import os
from . import views


    

urlpatterns = [
    # ✅ Authentication Routes
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.user_logout, name='logout'),

    # ✅ Application Routes (Protected)
     path('home/', views.home, name='home'),  # Default home page
    path('home/<int:user_id>/', views.home, name='home'),  # 🔥 New dynamic user home page

    path('famil/', views.family_view, name='famil'),
    path('appointments/', views.appointments, name='appointments'),
    path('journal/', views.journal_view, name='journal'),
    path('journal/confirmation/', lambda request: render(request, 'journal_confirmation.html'), name='journal_confirmation'),
    path('activity/', views.activity, name='activity'),
    path('settingscroll/', views.settingscroll, name='settingscroll'),
    path('addprofile/', views.add_profile, name='addprofile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('noactivity/', views.noactivity, name='noactivity'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
    path('rewards/', views.rewards, name='rewards'),
    path('symptom/', views.symptom, name='symptom'),
    path('nomedical/', views.nomedical, name='nomedical'),
    path('tour/', views.tour, name='tour'),
    path('med_aspirin/', views.med_aspirin, name='med_aspirin'),
    path('med_capsule/', views.med_capsule, name='med_capsule'),
    path('med_pill/', views.med_pill, name='med_pill'),
    path('med_schedule/', views.med_schedule, name='med_schedule'),
    path('medications/', views.medications, name='medications'),
    
    # ✅ Firebase Push Notification API
    path('save-token/', views.save_token, name='save-token'),

    # ✅ Serve firebase-messaging-sw.js Correctly
    re_path(r'^firebase-messaging-sw.js$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'happ/static'),
        'path': 'firebase-messaging-sw.js'
    }),
    path("chatbot-response/", chatbot_response, name="chatbot_response"),
]

# ✅ Serve static and media files correctly in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)