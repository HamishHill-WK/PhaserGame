const inputForm = document.getElementById('input-form');
const userInput = document.getElementById('user-input');
const outputDiv = document.getElementById('console-output');

inputForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const input = userInput.value.trim();
    if (!input) return;
    
    // Add simulation input to display
    addMessage('> ' + input, 'player-input');
    
    // Clear input field
    userInput.value = '';
    
    fetch('/LLMrequest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: input })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage('Error: ' + data.error, 'error-message');
        } else {
            // Add LLM response to display
            addMessage(data.message, 'llm-response');
        }
    })
    .catch(error => {
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
        
        console.log('ScrollHeight:', scrollHeight, 'NewHeight:', newHeight);
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
    const messageElements = outputDiv.querySelectorAll('div[class*="message"], div[class*="player-input"], div[class*="llm-response"], div[class*="system-message"], div[class*="error-message"]');
    
    messageElements.forEach(element => {
        messages.push({
            text: element.textContent,
            className: element.className
        });
    });
    
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
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