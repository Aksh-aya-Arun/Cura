// ✅ Use importScripts instead of ES Modules
importScripts("https://www.gstatic.com/firebasejs/11.3.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/11.3.1/firebase-messaging-compat.js");

// ✅ Firebase Configuration
firebase.initializeApp({
    apiKey: "AIzaSyD56BQB3E8okgh7FS9B7fgpPE1h6YRoJ8M",
    authDomain: "cura-b57a6.firebaseapp.com",
    projectId: "cura-b57a6",
    storageBucket: "cura-b57a6.appspot.com",
    messagingSenderId: "355005148675",
    appId: "1:355005148675:web:d36d7188ea55c90f89a836"
});

// ✅ Initialize Firebase Messaging
const messaging = firebase.messaging();

// ✅ Handle Background Push Notifications
messaging.onBackgroundMessage((payload) => {
    console.log("📩 Received background message: ", payload);
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: "/static/assets/images/icon.png",
    });
});
