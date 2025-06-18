class SecureGameExecutor {
    constructor() {
        // More precise patterns that avoid false positives
        this.dangerousPatterns = [
            {
                // Only match Function constructor calls, not function declarations
                pattern: /(?:new\s+)?Function\s*\(\s*['"`]/gi,
                message: "Function constructor with string parameter detected",
                explanation: "Only blocks Function('code') not function declarations"
            },
            {
                // Match standalone eval calls
                pattern: /(?:^|[^a-zA-Z0-9_$])eval\s*\(/gi,
                message: "eval() function call detected"
            },
            {
                // Match string-based setTimeout/setInterval
                pattern: /set(?:Timeout|Interval)\s*\(\s*['"`]/gi,
                message: "String-based timer function detected"
            },
            {
                // Match dangerous DOM operations
                pattern: /document\s*\.\s*(?:write|writeln)\s*\(/gi,
                message: "document.write detected"
            }
        ];
    }
    
    validateCode(code) {
        const violations = [];
        const lines = code.split('\n');
        
        lines.forEach((line, lineIndex) => {
            // Skip comments
            const trimmedLine = line.trim();
            if (trimmedLine.startsWith('//') || 
                trimmedLine.startsWith('/*') || 
                trimmedLine.startsWith('*')) {
                return;
            }
            
            this.dangerousPatterns.forEach(({ pattern, message }) => {
                const matches = [...line.matchAll(pattern)];
                matches.forEach(match => {
                    // Additional context check for Function pattern
                    if (message.includes('Function constructor')) {
                        // Make sure this isn't just a function declaration
                        const beforeMatch = line.substring(0, match.index).toLowerCase();
                        const afterMatch = line.substring(match.index + match[0].length);
                        
                        // Skip if this looks like a regular function
                        if (beforeMatch.includes('function ') || 
                            beforeMatch.endsWith('function') ||
                            line.toLowerCase().includes('function(') ||
                            line.toLowerCase().includes('function (')) {
                            return; // Don't flag this
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
}