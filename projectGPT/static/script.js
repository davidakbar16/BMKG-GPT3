document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.querySelector("#send-btn");
    const chatContainer = document.querySelector(".chat-container");
    const chatInput = document.querySelector("#chat-input");
    const themeButton = document.querySelector("#theme-btn");
    const deleteButton = document.querySelector("#delete-btn");

    async function handleOutgoingChat() {
        const userText = chatInput.value.trim();
        if (!userText) return;
        
   
        chatInput.value = '';
        chatInput.style.height = `${initialInputHeight}px`;

        const html = `<div class="chat-content">
                        <div class="chat-details">
                            <img src="../static/userlog.png" alt="user-img">
                            <p>${userText}</p>
                        </div>
                    </div>`;

        const outgoingChatDiv = createChatElement(html, "outgoing");
        chatContainer.querySelector(".default-text")?.remove();
        chatContainer.appendChild(outgoingChatDiv);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
        setTimeout(() => showBotMessage(userText), 500);
    }
    const showBotMessage = async (message) => {
        const html = `<div class="chat-content">
                        <div class="chat-details">
                            <img src="../static/Untitled.png" alt="chatbot-img">
                            <div class="typing-animation">
                                <div class="typing-dot" style="--delay: 0.2s"></div>
                                <div class="typing-dot" style="--delay: 0.3s"></div>
                                <div class="typing-dot" style="--delay: 0.4s"></div>
                            </div>
                        </div>
                        <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                    </div>`;
    
        const incomingChatDiv = createChatElement(html, "incoming");
        chatContainer.appendChild(incomingChatDiv);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    
        try {
            const answer = await getChatResponse(message);
            const pElement = document.createElement("p");
            pElement.textContent = answer;
            incomingChatDiv.querySelector(".typing-animation").remove();
            incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
        } catch (error) {
            const pElement = document.createElement("p");
            pElement.classList.add("error");
            pElement.textContent = error.message;
            incomingChatDiv.querySelector(".typing-animation").remove();
            incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
        }
    

        localStorage.setItem("all-chats", chatContainer.innerHTML);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    }

    async function getChatResponse(question) {
        try {
            
            const response = await fetch('/process_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok.');
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            return 'Maaf, terjadi kesalahan dalam memproses permintaan Anda.';
        }
    }

    function handleChatResponse(response) {
        const html = `<div class="chat-content">
                        <div class="chat-details">
                            <img src="../static/Untitled.png" alt="chatbot-img">
                            <div class="typing-animation">
                                <div class="typing-dot" style="--delay: 0.2s"></div>
                                <div class="typing-dot" style="--delay: 0.3s"></div>
                                <div class="typing-dot" style="--delay: 0.4s"></div>
                            </div>
                        </div>
                        <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                    </div>`;

        const chatDiv = createChatElement(html, 'incoming');
        chatContainer.appendChild(chatDiv);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
        
    }

    function createChatElement(content, className) {
        const chatDiv = document.createElement("div");
        chatDiv.classList.add("chat", className);
        chatDiv.innerHTML = content;
        return chatDiv;
    }

    function copyResponse(copyBtn) {
        const responseTextElement = copyBtn.parentElement.querySelector("div");
        navigator.clipboard.writeText(responseTextElement.textContent);
        copyBtn.textContent = "done";
        setTimeout(() => copyBtn.textContent = "content_copy", 1000);
    }

    deleteButton.addEventListener("click", () => {
        if (confirm("Are you sure you want to delete all the chats?")) {
            localStorage.removeItem("all-chats");
            loadDataFromLocalstorage();
        }
    });
    
    const showTypingAnimation = () => {
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="../static/Untitled.png" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                    <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                </div>`;
    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    getChatResponse(incomingChatDiv);
}

    themeButton.addEventListener("click", () => {
        document.body.classList.toggle("light-mode");
        localStorage.setItem("themeColor", themeButton.innerText);
        themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
    });

    function loadDataFromLocalstorage() {
        const themeColor = localStorage.getItem("themeColor");
        document.body.classList.toggle("light-mode", themeColor === "light_mode");
        themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

        const defaultText = `<div class="gradient-text">
                                <h1>BMKG-GPT</h1>
                                <p>Mulai Pertanyaan Seputar Informasi Meteorologi Klimatologi dan Geofisika.<br> Jelajahi InfoBMKG dengan Kekuatan AI.</p>
                            </div>`;

        chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    }

    const initialInputHeight = chatInput.scrollHeight;

    chatInput.addEventListener("input", () => {
        chatInput.style.height = `${initialInputHeight}px`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleOutgoingChat();
        }
    });

    loadDataFromLocalstorage();
    sendButton.addEventListener('click',handleOutgoingChat);
    
});