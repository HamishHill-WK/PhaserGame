inputForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const input = userInput.value.trim();
    if (!input) return;
    
    // Add simulation input to display
    addMessage('> ' + input, 'player-input');
    
    // Clear input field
    userInput.value = '';
    
    // Close any existing EventSource
    if (window.eventSource) {
        window.eventSource.close();
    }
    
    // Record start time for simulation
    const simulationStartTime = performance.now();
    let messageCount = 0;
    
    // Create a new EventSource for streaming
    console.log('Input:', input);
    const url = `/api/simulate_stream?simulation_input=${encodeURIComponent(input)}&npc_a=${encodeURIComponent(npcDropdownA.value)}&npc_b=${encodeURIComponent(npcDropdownB.value)}`;
    const eventSource = new EventSource(url);
    window.eventSource = eventSource;
    
    // Handle incoming message events
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            // Add the appropriate NPC's message to the display
            addMessage(`${data.speaker}: ${data.message}`, 'npc-response');
            messageCount++;
        } catch (error) {
            console.error('Error parsing SSE message:', error);
            addMessage(event.data, 'npc-response'); // Fallback to raw data
        }
    };
    
    // Handle end of conversation
    eventSource.addEventListener('end', function() {
        console.log('Conversation complete');
        const simulationTime = performance.now() - simulationStartTime;
        addMessage(`Simulation completed in ${simulationTime.toFixed(2)}ms (${messageCount} messages)`, 'system-message timing-info');
        eventSource.close();
    });
    
    // Handle errors
    eventSource.onerror = function() {
        console.error('SSE connection error');
        addMessage('Connection to server lost.', 'system-message');
        eventSource.close();
    };
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