// Dropdown functionality
const inputForm = document.getElementById('input-form');
const userInput = document.getElementById('user-input');
const outputDiv = document.getElementById('console-output');

function toggleDropdown() {
    const dropdown = document.getElementById("dropdown-content");
    dropdown.classList.toggle("show");
}

// Close dropdown when clicking outside
window.onclick = function(event) {
    if (!event.target.matches('.dropdown-btn') && !event.target.closest('.dropdown-content')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

// Handle checkbox changes
document.addEventListener('DOMContentLoaded', function() {
    // Load chat history when page loads
    loadChatFromStorage();
    
    // Add clear chat button functionality
    const clearChatButton = document.getElementById('clear-chat');
    if (clearChatButton) {
        clearChatButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear the chat history?')) {
                clearChatHistory();
            }
        });
    }
    
    Object.keys(taskDependencies).forEach(taskId => {
        const checkbox = document.getElementById(taskId);
        if (checkbox) {
            checkbox.addEventListener('click', function(event) {
                //event.preventDefault();
                const currentCheckedStatus = this.checked;
                handleTaskChange(taskId, currentCheckedStatus, !this.disabled, event);
            });
        }
    });
    resetTasks(); // Initialize settings on page load
});

let currentTask = "task1";

// Task dependencies - define which tasks depend on which
const taskDependencies = {
    'task1': [], // Task 1 - no dependencies
    'task2': ['task1'], // Task 2 depends on Task 1
    'task3': ['task1', 'task2'], // Task 3 depends on Tasks 1 & 2
    'task4': ['task1', 'task2', 'task3'], // Task 4 depends on 1, 2 & 3
    'task5': ['task1', 'task2', 'task3', 'task4'] // Task 5 depends on all previous
};

function addMessage(message, className, skipSave = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = className;
    messageDiv.textContent = message;
    outputDiv.appendChild(messageDiv);
    scrollToBottom();
    
    // Don't save system messages about restoration to avoid recursion
    if (!skipSave && !message.includes('Chat history restored')) {
        saveChatToStorage();
    }
}

function scrollToBottom() {
    if (outputDiv) {
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }
}

function resetTasks() {
    const t1 = document.getElementById('task1')
    t1.checked = false;
    t1.disabled = false; // Task 1 is always checkable

    const t2 = document.getElementById('task2');
    t2.checked = false;
    t2.disabled = true; // Disable Task 2 initially

    const t3 = document.getElementById('task3');
    t3.checked = false;
    t3.disabled = true; // Disable Task 3 initially

    const t4 = document.getElementById('task4');
    t4.checked = false;
    t4.disabled = true; // Disable Task 4 initially
    
    const t5 = document.getElementById('task5');
    t5.checked = false;
    t5.disabled = true; // Disable Task 5 initially
}

function handleTaskChange(taskId, currentCheckedStatus, enabled, event) {
    const dependencies = taskDependencies[taskId];
    console.log(`checking ${taskId}. Checking dependencies...`);
    let canCheck = true;

    dependencies.forEach(dep => {
        const depCheckbox = document.getElementById(dep);
        if (depCheckbox && !depCheckbox.checked) {
            canCheck = false; // Can uncheck if all dependencies are checked
        } 
    });

    if (canCheck) {
        // If no dependencies are checked, reset the task
        const selectedTask = document.getElementById(taskId);
        selectedTask.checked = true;
        console.warn(`checking ${taskId} due to met dependencies.`);
    }
    else{
        document.getElementById(taskId).checked = false;
        console.warn(`Cannot check ${taskId} due to unmet dependencies.`);
    }

    Object.keys(taskDependencies).forEach(dep => {
        const dependencies = taskDependencies[dep];
        let disabled = false;
        dependencies.forEach(dep => {
            const depCheckbox = document.getElementById(dep);
            if (depCheckbox && !depCheckbox.checked) {
                disabled = true; // Can uncheck if all dependencies are checked
            } 
        });
        const depCheckbox = document.getElementById(dep);
        if (depCheckbox && disabled === false) {
            depCheckbox.disabled = disabled;
            currentTask = depCheckbox.closest('label').textContent.trim(); // Update current task
            document.getElementById('current-task-text').innerText = `Current Task: ${currentTask}`;
        }
    });
}

function switchTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    console.log(`Switching to tab: ${tabName}`);
    console.log(`Current tabs: ${Array.from(tabs).map(tab => tab.id).join(', ')}`);
    
    tabs.forEach(tab => {
        console.log(`Checking tab: ${tab.id}`);
        if (tab.id === tabName) {
            tab.classList.add('active');
            tab.classList.remove('hidden');
            console.log(`Switched to tab: ${tabName}`);
        } else {
            tab.classList.remove('active');
            tab.classList.add('hidden');
            console.log(`Hiding tab: ${tab.id}`);
        }
    });

    // Update active tab button
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => {
        if (button.dataset.tab === tabName) {
            button.classList.add('selected-tab-button');
            button.classList.remove('not-active');
            console.log(`Button for tab ${tabName} is now active`);
        } else {
            button.classList.add('not-active');
            button.classList.remove('selected-tab-button');
            console.log(`Button for tab ${button.dataset.tab} is no longer active`);
        }
    });
}

// Chat persistence functionality
const CHAT_STORAGE_KEY = 'phaserGameChatHistory';

function saveChatToStorage() {
    const messages = [];
    const messageElements = outputDiv.querySelectorAll('div[class*="message"], div[class*="player-input"], div[class*="npc-response"], div[class*="system-message"], div[class*="error-message"]');
    
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
                  // Add a subtle notification that chat was restored
                setTimeout(() => {
                    addMessage(`Chat history restored (${messages.length} messages)`, 'system-message', true);
                }, 100);
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