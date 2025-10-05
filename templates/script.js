// --- GET REFERENCES TO ALL HTML ELEMENTS ---
const startScreen = document.getElementById('start-screen');
const startBtn = document.getElementById('start-btn');
const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const userInputForm = document.getElementById('user-input-form');
const userInput = document.getElementById('user-input');
const micBtn = document.getElementById('mic-btn');
const sendBtn = document.getElementById('send-btn');
const stopBtn = document.getElementById('stop-btn');

let typingTimer;

// --- EVENT LISTENER FOR THE START BUTTON ---
startBtn.addEventListener('click', () => {
    startScreen.classList.add('is-hidden');
    chatContainer.classList.remove('is-hidden');
    const greeting = "Hello! How can I help you today?";
    addMessageToChatbox(greeting, 'assistant');
    speak(greeting);
});

// --- TEXT-TO-SPEECH (SPEAKING) ---
function speak(text) {
    if (!text) {
        micBtn.disabled = false;
        sendBtn.disabled = false;
        return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onstart = () => {
        stopBtn.classList.remove('is-hidden');
        micBtn.classList.add('is-hidden');
    };
    utterance.onend = () => {
        micBtn.disabled = false;
        sendBtn.disabled = false;
        stopBtn.classList.add('is-hidden');
        micBtn.classList.remove('is-hidden');
    };
    speechSynthesis.speak(utterance);
}

// --- TYPEWRITER & ADD MESSAGE TO UI ---
function addMessageToChatbox(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);
    const textElement = document.createElement('p');
    if (sender === 'assistant') {
        let index = 0;
        textElement.textContent = "";
        clearTimeout(typingTimer);
        function typewriter() {
            if (index < message.length) {
                textElement.textContent += message.charAt(index);
                index++;
                chatBox.scrollTop = chatBox.scrollHeight;
                typingTimer = setTimeout(typewriter, 30);
            }
        }
        typewriter();
    } else {
        textElement.textContent = message;
    }
    messageElement.appendChild(textElement);
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// --- HANDLE SENDING MESSAGE TO BACKEND ---
async function handleUserMessage(message) {
    if (message.trim() === "") return;
    addMessageToChatbox(message, 'user');
    userInput.value = "";
    micBtn.disabled = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        if (data.action === 'open_url' && data.url) {
            window.open(data.url, '_blank');
        }
        
        const assistantMessage = data.text;
        addMessageToChatbox(assistantMessage, 'assistant');
        speak(assistantMessage);

    } catch (error) {
        console.error('Error:', error);
        const errorMessage = 'Sorry, something went wrong. Please check the terminal.';
        addMessageToChatbox(errorMessage, 'assistant');
        speak(errorMessage);
    }
}

// --- EVENT LISTENERS ---
userInputForm.addEventListener('submit', (event) => {
    event.preventDefault();
    handleUserMessage(userInput.value);
});

stopBtn.addEventListener('click', () => {
    speechSynthesis.cancel();
    clearTimeout(typingTimer);
    micBtn.disabled = false;
    sendBtn.disabled = false;
    stopBtn.classList.add('is-hidden');
    micBtn.classList.remove('is-hidden');
    console.log("Speech and typing stopped by click.");
});

// --- SPEECH RECOGNITION (LISTENING) ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    // NOTE: We are NOT setting recognition.lang, so it will use the browser's default.

    recognition.onresult = (event) => {
        const spokenText = event.results[0][0].transcript;
        handleUserMessage(spokenText);
    };
    recognition.onerror = (event) => {
        console.error(`Speech recognition error: ${event.error}`);
    };
    micBtn.addEventListener('click', () => {
        if (!micBtn.disabled) {
            try {
                recognition.start();
            } catch(e) { console.error("Could not start recognition:", e); }
        }
    });
} else {
    micBtn.style.display = 'none';
}