import { initializeApp } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-messaging.js";

// ✅ Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyD56BQB3E8okgh7FS9B7fgpPElh6YRoJ8M",
    authDomain: "cura-b57a6.firebaseapp.com",
    projectId: "cura-b57a6",
    storageBucket: "cura-b57a6.appspot.com",
    messagingSenderId: "355005148675",
    appId: "1:355005148675:web:d36d7188ea55c90f89a836"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// ✅ Register the Service Worker
navigator.serviceWorker.register('/firebase-messaging-sw.js')
    .then((registration) => {
        console.log("✅ Service Worker Registered:", registration);
    })
    .catch((error) => {
        console.error("❌ Service Worker Registration Failed:", error);
    });

// ✅ Request permission for notifications
Notification.requestPermission().then(permission => {
    if (permission === "granted") {
        console.log("🔔 Notification permission granted.");
        
        getToken(messaging, { vapidKey: "BPJafJV5Btzcwc9maY2whc-XANhWwMUrewp4IC8Sjo5KebKn_sdXYrLG-4bhaIknROGTzgnOLr5_oajyMXnLmAo" })
            .then(token => {
                if (token) {
                    console.log("📱 Device Token:", token);
                    sendTokenToServer(token); // ✅ Send token to Django
                } else {
                    console.warn("❌ No registration token available.");
                }
            })
            .catch(error => {
                console.error("🔥 Error fetching token:", error);
            });
    } else {
        console.warn("❌ Notification permission denied.");
    }
});

// ✅ Function to send the token to the Django backend
function sendTokenToServer(token) {
    fetch('/save-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() // ✅ Ensure CSRF token is handled
        },
        body: JSON.stringify({ token: token })
    })
    .then(response => response.json())
    .then(data => console.log("✅ Token saved on server:", data))
    .catch(error => console.error("❌ Error sending token:", error));
}

// ✅ Function to get CSRF token for Django
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}
