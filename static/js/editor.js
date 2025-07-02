let secureExecutor;

// Initialize the Ace editor
document.addEventListener('DOMContentLoaded', function() {

    secureExecutor = new SecureGameExecutor();

    const editor = ace.edit("editor");
    if (!editor) {
        console.error("Failed to initialize Ace editor.");
        return;
    }
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/javascript");

    fetch('/get-user-game-code')
      .then(response => response.json())
      .then(data => {
        if (data.success) {
            editor.setValue(data.code);
            editor.clearSelection();
        }
    });

    // Handle save button click
    document.getElementById('save-code').addEventListener('click', function() {
        const code = editor.getValue();

        try {
            secureExecutor.validateCode(code);
        } catch (error) {
            alert("Code validation failed: " + error.message);
            return;
        }

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
        })
         .catch(error => {
            console.error('Save error:', error);
            alert("Error saving code: " + error.message);
        });
    });
      // Handle reload button click
    document.getElementById('reload-game').addEventListener('click', function() {
        // Log game reload to backend
        fetch('/log-game-reload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
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
    fetch("/get-user-game-code")
        .then(response => response.json())
        .then(gameCode => {
            if (gameCode.success){
                try {
                    // Execute the new game code in a way that recreates the game
                    secureExecutor.executeSecurely(gameCode.code);
                    
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
            } else {
                if (typeof addMessage === 'function') {
                    addMessage('Error fetching game code: ' + data.error, 'error-message');
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