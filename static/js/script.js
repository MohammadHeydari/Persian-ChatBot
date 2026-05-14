document.addEventListener("DOMContentLoaded", () => {
    const sendButton = document.getElementById("send-btn");
    const inputField = document.getElementById("chat-input");


    sendButton.addEventListener("click", sendMessage);


    inputField.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});

async function sendMessage() {
    const inputField = document.getElementById('chat-input');
    const messageText = inputField.value.trim();
    
    if (!messageText) return;

    appendMessage(messageText, 'user');
    inputField.value = '';


    const botMessageDiv = appendMessage('', 'bot');

    try {
  
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: messageText })
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }


        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                break; 
            }
            
  
            const chunk = decoder.decode(value, { stream: true });
            

            botMessageDiv.innerHTML += chunk; 
            

            const chatBox = document.getElementById('chat-window');
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (error) {
        console.error("Fetch Error:", error);
        botMessageDiv.innerHTML = "متاسفانه خطایی در ارتباط با سرور رخ داد.";
    }
}

function appendMessage(text, sender) {
    const chatBox = document.getElementById('chat-window');
    const messageElement = document.createElement('div');
    
    messageElement.classList.add('message');
    if (sender === 'user') {
        messageElement.classList.add('user-msg');
    } else {
        messageElement.classList.add('bot-msg');
    }
    messageElement.innerHTML = text;
    
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return messageElement;
}