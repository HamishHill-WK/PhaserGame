// External Error Handler - Cannot be modified by participants
// This script monitors game.js execution and displays errors in the debug console

(function() {
    'use strict';
    
    // Error handling utilities for debug console
    function addToDebugConsole(message, type = 'info') {
        const debugConsole = document.getElementById('debug-console');
        if (!debugConsole) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `debug-entry debug-${type}`;
        logEntry.innerHTML = `<span class="debug-time">[${timestamp}]</span> <span class="debug-message">${message}</span>`;
        
        debugConsole.appendChild(logEntry);
        debugConsole.scrollTop = debugConsole.scrollHeight;
        
        // Limit console entries to prevent memory issues
        const entries = debugConsole.children;
        if (entries.length > 100) {
            debugConsole.removeChild(entries[0]);
        }
    }    function clearDebugConsole() {
        const debugConsole = document.getElementById('debug-console');
        if (debugConsole) {
            debugConsole.innerHTML = '';
        }
    }

    window.clearDebugConsole = clearDebugConsole;

    window.addEventListener('error', function(e) {
        // Check if error is from game.js
        const isGameError = e.filename && e.filename.includes('game.js');
        const errorLocation = isGameError ? 'game.js' : (e.filename || 'unknown');
        
        const errorMsg = `JavaScript Error in ${errorLocation}: ${e.message} (line ${e.lineno - 4})`;
        addToDebugConsole(errorMsg, 'error');
        console.error('Detected Error:', e);
        
        return false;
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        const errorMsg = `Unhandled Promise Rejection: ${e.reason}`;
        addToDebugConsole(errorMsg, 'error');
        console.error('Unhandled Promise Rejection:', e);
    });

    let gameInitialized = false;
    let initCheckInterval;

    function monitorGameInitialization() {        initCheckInterval = setInterval(function() {
            if (window.game && !gameInitialized) {
                gameInitialized = true;
                
                // Setup Phaser-specific error monitoring
                if (window.game.events) {
                    window.game.events.on('error', function(error) {
                        const errorMsg = `Phaser Error: ${error.message || error}`;
                        addToDebugConsole(errorMsg, 'error');
                    });
                }
                  // Monitor scene events
                if (window.game.scene && window.game.scene.scenes[0]) {
                    const scene = window.game.scene.scenes[0];
                }
                
                clearInterval(initCheckInterval);
            }
        }, 100);
          // Stop checking after 10 seconds
        setTimeout(function() {
            if (initCheckInterval) {
                clearInterval(initCheckInterval);
            }
        }, 10000);
    }

    const originalConsoleError = console.error;
    console.error = function(...args) {
        // Call original console.error
        originalConsoleError.apply(console, args);
        
        // Add to debug console if it looks like a game error
        const errorMessage = args.join(' ');
        if (errorMessage.toLowerCase().includes('game') || 
            errorMessage.toLowerCase().includes('phaser') || 
            errorMessage.toLowerCase().includes('scene')) {            addToDebugConsole(`Console Error: ${errorMessage}`, 'error');
        }
    };
    function checkGameScriptLoaded() {
        // Check if expected game objects exist
        setTimeout(function() {
            if (typeof Breakout === 'undefined') {
                addToDebugConsole('Syntax Error: Breakout class not found - check game.js for syntax errors', 'error');
            } 
            // Additional checks for common game objects
            if (typeof Phaser === 'undefined') {
                addToDebugConsole('Error: Phaser library not loaded', 'error');
            }
        }, 500);
    }

    // Monitor script loading errors
    function monitorScriptLoading() {
        // Override the script error event for the game script specifically
        const scripts = document.querySelectorAll('script[src*="game.js"]');
        scripts.forEach(script => {
            script.addEventListener('error', function(e) {
                addToDebugConsole('Failed to load game.js - check for syntax errors', 'error');
            });        });
    }    // Initialize monitoring when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        monitorScriptLoading();
        monitorGameInitialization();
        checkGameScriptLoaded();
    });

    // Monitor for game reload events
    let originalReload;
    if (typeof reloadGame === 'function') {
        originalReload = reloadGame;
        window.reloadGame = function() {
            addToDebugConsole('Game reload initiated', 'info');
            gameInitialized = false;
            monitorGameInitialization();
            return originalReload.apply(this, arguments);
        };
    }

    // Add a function to inject custom monitoring into user's game code
    window.logGameEvent = function(message, type = 'info') {
        addToDebugConsole(`Game Event: ${message}`, type);
    };

})();
