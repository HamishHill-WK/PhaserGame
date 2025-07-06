const inputForm = document.getElementById('input-form');
const userInput = document.getElementById('user-input');
const outputDiv = document.getElementById('console-output');

function addMessage(message, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = className;

    if (className === 'llm-response' || className === 'llm-code') {
        messageDiv.innerHTML = marked.parse(message);
    }
    else{
        messageDiv.textContent = message;
    }

    outputDiv.appendChild(messageDiv);
    scrollToBottom();
    saveChatToStorage();
}

function scrollToBottom() {
    if (outputDiv) {
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }
}

inputForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const input = userInput.value.trim();
    const context = getAllMessages();
    const extendedThinking = document.getElementById('extended-thinking-checkbox')?.checked || false;
    console.log('chat.js: Context:', context);
    if (!input) return;
    
    // Add simulation input to display
    addMessage('> ' + input, 'player-input');
    
    // Clear input field
    userInput.value = '';
    
    // Show loading message
    const loadingId = 'llm-loading-message';
    let loadingDiv = document.createElement('div');
    loadingDiv.className = 'llm-response';
    loadingDiv.id = loadingId;
    loadingDiv.textContent = 'AI is thinking...';
    outputDiv.appendChild(loadingDiv);
    scrollToBottom();
    
    fetch('/LLMrequest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            context : context,
            input: input,
            extended_thinking: extendedThinking })
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading message
        const loadingElem = document.getElementById(loadingId);
        if (loadingElem) loadingElem.remove();
        if (data.error) {
            addMessage('Error: ' + data.error, 'error-message');
        } else {
            // Add LLM response to display
            console.log('chat.js: LLM Response:', typeof(data), data);
            data.forEach(element => {
                console.log('Element:', element);
                if (element[0] === 'text') {
                    addMessage(element[1], 'llm-response');
                }
                if (element[0] === 'code') {
                    addMessage(element[1], 'llm-code');
                }
            });
        }
    })
    .catch(error => {
        // Remove loading message
        const loadingElem = document.getElementById(loadingId);
        if (loadingElem) loadingElem.remove();
        console.error('Error:', error);
        addMessage('Error: ' + error.message, 'error-message');
    });
});

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('user-input');
    
    // ...existing code...
    function autoResize() {
        const textarea = document.getElementById('user-input');
        const scrollHeight = textarea.scrollHeight;
        const minHeight = 100;
        const maxHeight = 200; // Set this to what you want (much smaller than 450px)
        
        const newHeight = Math.max(minHeight, Math.min(scrollHeight, maxHeight));
        textarea.style.height = newHeight + 'px';
        
        // Show scrollbar if content exceeds max height
        if (scrollHeight > maxHeight) {
            textarea.style.overflowY = 'auto';
        } else {
            textarea.style.overflowY = 'hidden';
        }
    }
    
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            if (e.shiftKey) {
                return;
            }
            e.preventDefault(); // Prevent new line
            inputForm.dispatchEvent(new Event('submit')); // Trigger form submission
            textarea.value = ''; // Clear input after submission
            textarea.style.height = '100px'; // Reset height to initial value
        }
    });

    textarea.addEventListener('input', autoResize);
    textarea.addEventListener('paste', function() {
        setTimeout(autoResize, 0);
    });
    
    // Initial resize
    autoResize();
});

// Chat persistence functionality
const CHAT_STORAGE_KEY = 'phaserGameChatHistory';
//chat is stored in the browser so it is unique to each user
function saveChatToStorage() {
    const messages = [];
    const messageElements = getAllMessages();
    
    messageElements.forEach(element => {
        messages.push({
            text: element.textContent,
            className: element.className
        });
    });
    
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
}

function getAllMessages(){
    return outputDiv.querySelectorAll('div[class*="message"], div[class*="player-input"], div[class*="llm-response"], div[class*="llm-code"], div[class*="system-message"], div[class*="error-message"]');
}

function loadChatFromStorage() {
    const savedMessages = localStorage.getItem(CHAT_STORAGE_KEY);
    if (savedMessages) {
        try {
            const messages = JSON.parse(savedMessages);
            if (messages.length > 0) {
                messages.forEach(message => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = message.className;
                    messageDiv.textContent = message.text;
                    outputDiv.appendChild(messageDiv);
                });
                scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
}

function clearChatHistory() {
    localStorage.removeItem(CHAT_STORAGE_KEY);
    outputDiv.innerHTML = '';
}