class SecureGameExecutor {
    constructor() {
        this.allowedGlobals = new Set([
            'Phaser', 'console', 'Math', 'parseInt', 'parseFloat', 
            'isNaN', 'isFinite', 'JSON', 'Date', 'Array', 'Object',
            'Number', 'String', 'Boolean', 'Promise', 'Set', 'Map',
            'WeakSet', 'WeakMap', 'Symbol', 'Proxy', 'Reflect'
        ]);
        
        this.bannedPatterns = [
            // Code injection patterns
            {
                pattern: /(?:^|[^a-zA-Z0-9_$])eval\s*\(/gi,
                message: "eval() function call detected",
                severity: "CRITICAL"
            },
            {
                pattern: /(?:new\s+)?Function\s*\(\s*['"`]/gi,
                message: "Function constructor with string parameter detected",
                severity: "CRITICAL"
            },
            {
                pattern: /window\s*\[\s*['"`]eval['"`]\s*\]/gi,
                message: "Indirect eval access via window object",
                severity: "CRITICAL"
            },
            {
                pattern: /var\s+\w+\s*=\s*eval\s*;/gi,
                message: "eval assignment to variable",
                severity: "CRITICAL"
            },
            
            // Timer-based injection
            {
                pattern: /set(?:Timeout|Interval)\s*\(\s*['"`]/gi,
                message: "String-based timer function detected",
                severity: "HIGH"
            },
            
            // DOM manipulation
            {
                pattern: /document\s*\.\s*(?:write|writeln)\s*\(/gi,
                message: "document.write/writeln detected",
                severity: "HIGH"
            },
            {
                pattern: /document\s*\.\s*(?:body|head)\s*\.\s*innerHTML\s*=/gi,
                message: "innerHTML assignment to document body/head",
                severity: "HIGH"
            },
            
            // Prototype pollution
            {
                pattern: /__proto__\s*\./gi,
                message: "__proto__ manipulation detected",
                severity: "HIGH"
            },
            {
                pattern: /Object\s*\.\s*prototype\s*\./gi,
                message: "Object.prototype manipulation detected",
                severity: "HIGH"
            },
            {
                pattern: /constructor\s*\.\s*prototype\s*\./gi,
                message: "constructor.prototype access detected",
                severity: "HIGH"
            },
            
            // Global object access
            {
                pattern: /(?:window|self|top|parent)\s*\.\s*location\s*=/gi,
                message: "Location assignment detected",
                severity: "HIGH"
            },
            {
                pattern: /globalThis\s*\./gi,
                message: "globalThis access detected",
                severity: "HIGH"
            },
            
            // Storage access
            {
                pattern: /(?:local|session)Storage\s*\./gi,
                message: "Web storage access detected",
                severity: "MEDIUM"
            },
            
            // Network access
            {
                pattern: /\bfetch\s*\(/gi,
                message: "fetch() API call detected",
                severity: "HIGH"
            },
            {
                pattern: /new\s+XMLHttpRequest\s*\(/gi,
                message: "XMLHttpRequest instantiation detected",
                severity: "HIGH"
            },
            {
                pattern: /\bimport\s*\(/gi,
                message: "Dynamic import() detected",
                severity: "HIGH"
            },
            
            // Obfuscation patterns
            {
                pattern: /\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}/g,
                message: "Unicode escape obfuscation detected",
                severity: "HIGH"
            },
            {
                pattern: /\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}/g,
                message: "Hex escape obfuscation detected",
                severity: "HIGH"
            }
        ];
        
        // Maximum code size (50KB)
        this.maxCodeSize = 50000;
        
        // Maximum string concatenations (to detect obfuscation)
        this.maxStringConcats = 15;
        
        // Entropy threshold for obfuscation detection
        this.maxEntropy = 4.5;
    }
    
    validateCode(code) {
        const violations = [];
        const warnings = [];
        
        // Size check
        if (code.length > this.maxCodeSize) {
            violations.push(`Code too large: ${code.length} bytes (max ${this.maxCodeSize})`);
        }
        
        // String concatenation check
        const concatCount = (code.match(/['""][^'"]*\+/g) || []).length;
        if (concatCount > this.maxStringConcats) {
            violations.push(`Excessive string concatenation: ${concatCount} (max ${this.maxStringConcats})`);
        }
        
        // Pattern matching
        const lines = code.split('\n');
        lines.forEach((line, lineIndex) => {
            const trimmedLine = line.trim();
            
            // Skip comments
            if (trimmedLine.startsWith('//') || 
                trimmedLine.startsWith('/*') || 
                trimmedLine.startsWith('*')) {
                return;
            }
            
            this.bannedPatterns.forEach(({pattern, message, severity}) => {
                const matches = [...line.matchAll(pattern)];
                matches.forEach(match => {
                    const violation = {
                        line: lineIndex + 1,
                        column: match.index + 1,
                        message: message,
                        severity: severity,
                        context: line.trim()
                    };
                    
                    if (severity === 'CRITICAL' || severity === 'HIGH') {
                        violations.push(`Line ${violation.line}: ${violation.message}`);
                    } else {
                        warnings.push(`Line ${violation.line}: ${violation.message}`);
                    }
                });
            });
        });
        
        // Entropy analysis
        const entropy = this.calculateEntropy(code);
        if (entropy > this.maxEntropy) {
            violations.push(`High entropy detected (possible obfuscation): ${entropy.toFixed(2)}`);
        }
        
        return {
            isValid: violations.length === 0,
            violations: violations,
            warnings: warnings,
            entropy: entropy,
            codeSize: code.length,
            details: {
                stringConcatenations: concatCount,
                linesAnalyzed: lines.length
            }
        };
    }
    
    calculateEntropy(code) {
        if (!code) return 0;
        
        const charCounts = {};
        for (let char of code) {
            charCounts[char] = (charCounts[char] || 0) + 1;
        }
        
        const codeLength = code.length;
        let entropy = 0;
        
        for (let count of Object.values(charCounts)) {
            const probability = count / codeLength;
            if (probability > 0) {
                entropy -= probability * Math.log2(probability);
            }
        }
        
        return entropy;
    }
    
    executeSecurely(code) {
        try {
            // Comprehensive validation first
            const validation = this.validateCode(code);
            
            if (!validation.isValid) {
                const error = new Error(`Security validation failed: ${validation.violations.join(', ')}`);
                error.violations = validation.violations;
                error.warnings = validation.warnings;
                throw error;
            }
            
            // Log warnings even if code passes
            if (validation.warnings.length > 0) {
                this.logToDebugConsole('warn', `Security warnings: ${validation.warnings.join(', ')}`);
            }
            
            // Create secure execution context
            this.createSecureContext(code);
            
        } catch (error) {
            this.logToDebugConsole('error', `Security validation failed: ${error.message}`);
            throw error;
        }
    }
    
    createSecureContext(code) {
        // Create isolated iframe for execution
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.sandbox = 'allow-scripts allow-same-origin';
        iframe.id = 'secure-game-frame';
        
        // Clean up any existing iframe
        const existingFrame = document.getElementById('secure-game-frame');
        if (existingFrame) {
            existingFrame.remove();
        }
        
        document.body.appendChild(iframe);
        
        try {
            const iframeWindow = iframe.contentWindow;
            const iframeDocument = iframe.contentDocument;
            
            // Create the game container in the iframe
            iframeDocument.body.innerHTML = '<div id="game-container"></div>';
            
            // Provide only safe globals to iframe
            const safeContext = this.createSafeContext(iframeWindow);
            
            // Execute code in restricted context
            const wrappedCode = this.wrapSecureCode(code, safeContext);
            
            // Execute in iframe context
            iframeWindow.eval(wrappedCode);
            
            // Move the game canvas to main document
            this.moveGameToMainDocument(iframeDocument);
            
        } catch (error) {
            this.logToDebugConsole('error', `Execution error: ${error.message}`);
            throw error;
        } finally {
            // Clean up iframe after a delay
            setTimeout(() => {
                if (iframe && iframe.parentNode) {
                    iframe.remove();
                }
            }, 1000);
        }
    }
    
    createSafeContext(iframeWindow) {
        const safeContext = {};
        
        // Add safe globals
        for (let global of this.allowedGlobals) {
            if (window[global]) {
                safeContext[global] = window[global];
            }
        }
        
        // Provide restricted console
        safeContext.console = {
            log: (...args) => this.logToDebugConsole('info', args.join(' ')),
            error: (...args) => this.logToDebugConsole('error', args.join(' ')),
            warn: (...args) => this.logToDebugConsole('warn', args.join(' ')),
            info: (...args) => this.logToDebugConsole('info', args.join(' '))
        };
        
        // Provide safe window object with limited properties
        safeContext.window = {
            game: null, // Will be set by Phaser
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight
        };
        
        return safeContext;
    }
    
    wrapSecureCode(code, safeContext) {
        const contextKeys = Object.keys(safeContext);
        
        return `
            (function(${contextKeys.join(', ')}) {
                "use strict";
                
                // Block access to dangerous globals
                var eval = undefined;
                var Function = undefined;
                var constructor = undefined;
                var __proto__ = undefined;
                var prototype = undefined;
                var document = undefined; 
                var localStorage = undefined;
                var sessionStorage = undefined;
                var XMLHttpRequest = undefined;
                var fetch = undefined;
                var import = undefined;
                var require = undefined;
                var process = undefined;
                var global = undefined;
                var globalThis = undefined;
                var self = undefined;
                var parent = undefined;
                var top = undefined;
                
                // Provide safe window reference
                var window = arguments[${contextKeys.indexOf('window')}];
                
                try {
                    ${code}
                } catch (error) {
                    console.error("Game execution error:", error.message);
                    throw error;
                }
                
            })(${contextKeys.map(key => `safeContext.${key}`).join(', ')});
        `.replace(/safeContext\./g, 'arguments[arguments.length - 1].');
    }
    
    moveGameToMainDocument(iframeDocument) {
        // Find the Phaser canvas in iframe
        const iframeCanvas = iframeDocument.querySelector('canvas');
        const mainGameContainer = document.getElementById('game-container');
        
        if (iframeCanvas && mainGameContainer) {
            // Clear main container
            mainGameContainer.innerHTML = '';
            
            // Clone canvas to main document
            const clonedCanvas = iframeCanvas.cloneNode(true);
            mainGameContainer.appendChild(clonedCanvas);
            
            // Update window.game reference
            if (window.Phaser && iframeDocument.defaultView.game) {
                window.game = iframeDocument.defaultView.game;
            }
        }
    }
    
    logToDebugConsole(level, message) {
        // Use existing debug console function if available
        if (typeof addToDebugConsole === 'function') {
            addToDebugConsole(message, level);
        } else {
            // Fallback to direct DOM manipulation
            const debugConsole = document.getElementById('debug-console');
            if (debugConsole) {
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = `debug-entry debug-${level}`;
                logEntry.innerHTML = `<span class="debug-time">[${timestamp}]</span> <span class="debug-message">${message}</span>`;
                debugConsole.appendChild(logEntry);
                debugConsole.scrollTop = debugConsole.scrollHeight;
                
                // Limit entries
                const entries = debugConsole.children;
                if (entries.length > 100) {
                    debugConsole.removeChild(entries[0]);
                }
            } else {
                // Fallback to browser console
                console[level] ? console[level](message) : console.log(message);
            }
        }
    }
}

// Make globally available
window.SecureGameExecutor = SecureGameExecutor;