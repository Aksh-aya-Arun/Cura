// Toggle chatbot visibility
function toggleChatbot() {
    let chatbotIcon = document.getElementById("chatbot-icon");
    let chatbotBox = document.getElementById("chatbot-box");

    if (chatbotBox.style.display === "block") {
        chatbotBox.style.display = "none";
        chatbotIcon.style.display = "block";
    } else {
        chatbotBox.style.display = "block";
        chatbotIcon.style.display = "none";
    }
}

// Display initial messages when chatbot opens
function initiateChat() {
    let messagesContainer = document.getElementById("chatbot-messages");
    messagesContainer.innerHTML = `
        <p class="bot-message">👋 Hi! Welcome to Cura Chatbot.</p>
        <p class="bot-message">Let's get started! How are you feeling today?</p>
    `;
}

// Handle user input
function handleChatbotInput(event) {
    if (event.key === "Enter") {
        let inputField = document.getElementById("chatbot-input");
        let message = inputField.value.trim();
        if (message) {
            displayMessage(message, "user");
            showTypingIndicator(); // Show "..." before bot responds
            setTimeout(() => {
                getChatbotResponse(message);
            }, 2000); // Delay response by 2 seconds
            inputField.value = "";
        }
    }
}

// Display chat messages
function displayMessage(message, sender) {
    let messageContainer = document.createElement("p");
    messageContainer.className = sender === "user" ? "user-message" : "bot-message";
    messageContainer.textContent = message;
    document.getElementById("chatbot-messages").appendChild(messageContainer);
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    let messagesContainer = document.getElementById("chatbot-messages");
    let typingIndicator = document.createElement("p");
    typingIndicator.className = "bot-message typing-indicator";
    typingIndicator.textContent = "...";
    typingIndicator.id = "typing-indicator";
    messagesContainer.appendChild(typingIndicator);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    let typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Fetch chatbot response with delay
function getChatbotResponse(message) {
    fetch("/chatbot_query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        removeTypingIndicator(); // Remove "..." before showing bot's response
        displayMessage(data.answer, "bot");
    })
    .catch(error => {
        console.error("Error:", error);
        removeTypingIndicator();
        displayMessage("Sorry, I couldn't process that.", "bot");
    });
}

// Scroll to the latest message
function scrollToBottom() {
    let messagesContainer = document.getElementById("chatbot-messages");
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Open chatbot and start the conversation
document.addEventListener("DOMContentLoaded", initiateChat);