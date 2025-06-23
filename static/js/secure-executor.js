class SecureGameExecutor {
    constructor() {
        this.allowedGlobals = ['Phaser', 'Math', 'Date', 'JSON', 'parseInt', 'parseFloat', 'Number', 'String', 'Array', 'Object'];
        
        // Your existing dangerous patterns
        this.dangerousPatterns = [
            {
                pattern: /(?:new\s+)?Function\s*\(\s*['"`]/gi,
                message: "Function constructor with string parameter detected"
            },
            {
                pattern: /(?:^|[^a-zA-Z0-9_$])eval\s*\(/gi,
                message: "eval() function call detected"
            },
            {
                pattern: /set(?:Timeout|Interval)\s*\(\s*['"`]/gi,
                message: "String-based timer function detected"
            },
            {
                pattern: /document\s*\.\s*(?:write|writeln)\s*\(/gi,
                message: "document.write detected"
            },
            // Add more patterns for public-facing
            {
                pattern: /fetch\s*\(/gi,
                message: "fetch() detected - network requests blocked"
            },
            {
                pattern: /XMLHttpRequest/gi,
                message: "XMLHttpRequest detected"
            },
            {
                pattern: /innerHTML\s*=/gi,
                message: "innerHTML assignment detected"
            }
        ];
    }
    
    validateCode(code) {
        const violations = [];
        const lines = code.split('\n');
        
        lines.forEach((line, lineIndex) => {
            const trimmedLine = line.trim();
            if (trimmedLine.startsWith('//') || 
                trimmedLine.startsWith('/*') || 
                trimmedLine.startsWith('*')) {
                return;
            }
            
            this.dangerousPatterns.forEach(({ pattern, message }) => {
                const matches = [...line.matchAll(pattern)];
                matches.forEach(match => {
                    if (message.includes('Function constructor')) {
                        const beforeMatch = line.substring(0, match.index).toLowerCase();
                        if (beforeMatch.includes('function ') || 
                            beforeMatch.endsWith('function') ||
                            line.toLowerCase().includes('function(') ||
                            line.toLowerCase().includes('function (')) {
                            return;
                        }
                    }
                    
                    violations.push({
                        line: lineIndex + 1,
                        column: match.index + 1,
                        message: message,
                        context: line.trim()
                    });
                });
            });
        });
        
        return {
            isValid: violations.length === 0,
            violations: violations
        };
    }

    executeSecurely(code) {
        try {
            // Validation first
            const validation = this.validateCode(code);
            
            if (!validation.isValid) {
                const errorMessages = validation.violations.map(v => 
                    `Line ${v.line}: ${v.message}`
                ).join('\n');
                throw new Error(`Security validation failed:\n${errorMessages}`);
            }
            
            // Execute code securely
            this.secureExecute(code);
            
        } catch (error) {
            this.logToDebugConsole('error', `Security validation failed: ${error.message}`);
            throw error;
        }
    }

    secureExecute(code) {
        // Remove old script to prevent conflicts
        const oldScript = document.getElementById('secure-game-script');
        if (oldScript) {
            oldScript.remove();
        }

        try {
            // Create script element with proper source mapping for line numbers
            const script = document.createElement('script');
            script.id = 'secure-game-script';
            script.type = 'text/javascript';
            
            // Wrap code in a controlled execution context
            const wrappedCode = this.wrapCodeForExecution(code);
            script.textContent = wrappedCode + '\n//# sourceURL=game.js';
            
            // Execute by appending to head
            document.head.appendChild(script);
            
            this.logToDebugConsole('info', 'Code executed successfully');
            
        } catch (executionError) {
            this.logToDebugConsole('error', `Execution failed: ${executionError.message}`);
            throw executionError;
        }
    }

    wrapCodeForExecution(code) {
        // For public-facing, wrap in try-catch for better error handling
        return `
(function() {
    'use strict';
    try {
        ${code}
    } catch (error) {
        if (typeof addToDebugConsole === 'function') {
            addToDebugConsole('Runtime Error: ' + error.message + ' (line ' + (error.lineNumber || 'unknown') + ')', 'error');
        }
        console.error('Game execution error:', error);
        throw error;
    }
})();
        `;
    }

    logToDebugConsole(level, message) {
        if (typeof addToDebugConsole === 'function') {
            addToDebugConsole(message, level);
        } else {
            const debugConsole = document.getElementById('debug-console');
            if (debugConsole) {
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = `debug-entry debug-${level}`;
                logEntry.innerHTML = `<span class="debug-time">[${timestamp}]</span> <span class="debug-message">${message}</span>`;
                debugConsole.appendChild(logEntry);
                debugConsole.scrollTop = debugConsole.scrollHeight;
                
                if (debugConsole.children.length > 100) {
                    debugConsole.removeChild(debugConsole.children[0]);
                }
            } else {
                console[level] ? console[level](message) : console.log(message);
            }
        }
    }

    // Keep this for future iframe implementation if needed
    createSecureContext() {
        const safeContext = {};
        
        for (let global of this.allowedGlobals) {
            if (window[global]) {
                safeContext[global] = window[global];
            }
        }
        
        safeContext.console = {
            log: (...args) => this.logToDebugConsole('info', args.join(' ')),
            error: (...args) => this.logToDebugConsole('error', args.join(' ')),
            warn: (...args) => this.logToDebugConsole('warn', args.join(' ')),
            info: (...args) => this.logToDebugConsole('info', args.join(' '))
        };
        
        safeContext.window = {
            game: null,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight
        };
        
        return safeContext;
    }
}