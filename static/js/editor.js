// Initialize the Ace editor
document.addEventListener('DOMContentLoaded', function() {
    const editor = ace.edit("editor");
    if (!editor) {
        console.error("Failed to initialize Ace editor.");
        return;
    }
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/javascript");
    
    // Fetch current game.js content
    fetch("/static/js/game.js")
        .then(response => response.text())
        .then(data => {
            editor.setValue(data);
            editor.clearSelection();
        });
        
    // Handle save button click
    document.getElementById('save-code').addEventListener('click', function() {
        const code = editor.getValue();

            console.log('=== SAVE DEBUG ===');
    console.log('Code length:', code.length);
    console.log('Number of lines:', code.split('\n').length);
    console.log('Ends with newline:', code.endsWith('\n'));
    console.log('Ends with multiple newlines:', /\n{2,}$/.test(code));
    console.log('Last 100 chars:', JSON.stringify(code.slice(-100)));
    
        
        fetch("/save-code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ code: code, file: "game.js" })
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert("Code saved successfully!");
            } else {
                alert("Error saving code: " + data.error);
            }
        });
    });
      // Handle reload button click
    document.getElementById('reload-game').addEventListener('click', function() {
        reloadGame();
    });
});

// Function to reload game without refreshing the page
function reloadGame() {
    // Destroy existing Phaser game instance if it exists
    if (window.game) {
        window.game.destroy(true);
        window.game = null;
    }
    
    // Clear the game container
    const gameContainer = document.getElementById('game-container');
    gameContainer.innerHTML = '';
    
    clearDebugConsole();

    // Reload and re-execute the game script
    fetch("/static/js/game.js")
        .then(response => response.text())
        .then(gameCode => {
            try {
                // Execute the new game code in a way that recreates the game
                eval(gameCode);
                
                // Add success message to chat
                if (typeof addMessage === 'function') {
                    addMessage('Game reloaded successfully!', 'system-message');
                }
            } catch (error) {
                console.error('Error executing game code:', error);
                if (typeof addMessage === 'function') {
                    addMessage('Error reloading game: ' + error.message, 'error-message');
                }
            }
        })
        .catch(error => {
            console.error('Error fetching game code:', error);
            if (typeof addMessage === 'function') {
                addMessage('Error fetching game code: ' + error.message, 'error-message');
            }
        });
}

function loadGameScript() {
    const editor = ace.edit("editor");
    if (!editor) {
        console.error("Failed to initialize Ace editor.");
        return;
    }
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/javascript");
    
    // Fetch current game.js content
    fetch("/static/js/game.js")
        .then(response => response.text())
        .then(data => {
            editor.setValue(data);
            editor.clearSelection();
        });
        // Handle save button click
    document.getElementById('save-code').addEventListener('click', function() {
        const code = editor.getValue();
        
        fetch("/save-code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ code: code, file: "game.js" })
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert("Code saved successfully!");
            } else {
                alert("Error saving code: " + data.error);
            }
        });
    });
    
}