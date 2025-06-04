// Initialize the Ace editor
document.addEventListener('DOMContentLoaded', function() {
    const editor = ace.edit("editor");
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
    
    // Handle reload button click
    document.getElementById('reload-game').addEventListener('click', function() {
        location.reload();
    });
});
