# Security Testing System

This directory contains a comprehensive security testing suite for validating the game code security system. The testing suite includes multiple attack vectors and validation methods to ensure malicious code is properly blocked while allowing legitimate game development.

## 🔒 Security Testing Components

### 1. Backend Security Validation (`app.py`)
- **EnhancedSecurityValidator**: Comprehensive Python-based validation
- Pattern matching for dangerous code constructs
- AST (Abstract Syntax Tree) analysis
- Entropy analysis for obfuscation detection
- Size limits and concatenation checks

### 2. Frontend Security Execution (`static/js/secure-executor.js`)
- **SecureGameExecutor**: Client-side code validation and sandboxed execution
- Iframe-based isolation
- Global object restriction
- Real-time pattern detection

### 3. Comprehensive Test Suite (`static/js/security-tester.js`)
- **SecurityTester**: JavaScript-based testing framework
- 40+ malicious code patterns
- Legitimate game code samples
- Performance and entropy analysis

### 4. Command Line Test Runners

#### Quick Test (`quick_security_test.py`)
```bash
python quick_security_test.py
```
Fast validation of critical attack vectors.

#### Comprehensive Test (`security_test_runner.py`)
```bash
# Run all tests
python security_test_runner.py --verbose

# Run only malicious code tests
python security_test_runner.py --malicious-only

# Run only benign code tests  
python security_test_runner.py --benign-only

# Export detailed HTML report
python security_test_runner.py --export-report security_report.html

# JSON output for automation
python security_test_runner.py --json
```

### 5. Web-Based Testing Interface

#### Security Test Dashboard (`/security-test-ui`)
- Interactive web interface for security testing
- Real-time test execution
- Visual results with statistics
- Custom code testing functionality

#### Security Test API (`/security-test`)
- RESTful endpoint for automated testing
- JSON input/output for integration
- Detailed validation results

## 🚨 Attack Vectors Tested

### Code Injection
- `eval()` function calls
- `Function()` constructor abuse
- Indirect eval via `window['eval']`
- Variable-based eval assignments

### Timer-Based Injection
- `setTimeout()` with string parameters
- `setInterval()` with string parameters

### DOM Manipulation
- `document.write()` / `document.writeln()`
- `innerHTML` injection attacks
- Script tag injection

### Prototype Pollution
- `Object.prototype` manipulation
- `__proto__` property access
- `constructor.prototype` attacks

### Global Object Access
- `window.location` hijacking
- `globalThis` access
- Frame navigation attacks

### Storage Manipulation
- `localStorage` access
- `sessionStorage` manipulation

### Network Access
- `fetch()` API calls
- `XMLHttpRequest` usage
- Dynamic `import()` attacks

### Obfuscation Techniques
- Unicode escape sequences
- Hex escape sequences
- String concatenation obfuscation
- Base64 encoding tricks

### Resource Exhaustion
- Infinite loops
- Memory exhaustion
- Recursive function bombs

### Advanced Evasion
- `toString()` method override
- `valueOf()` method exploitation
- `Symbol.toPrimitive` attacks
- Proxy handler injection

## ✅ Legitimate Code Patterns

The system validates that these legitimate game development patterns are **not** blocked:

- Standard function declarations
- Phaser.js game setup code
- Safe timer usage (with function references)
- Mathematical calculations
- Array and object manipulation
- Event handlers and callbacks
- Canvas operations
- Game physics calculations

## 📊 Test Results Interpretation

### Security Effectiveness Metrics
- **Malicious Block Rate**: Percentage of dangerous code correctly blocked
- **False Positive Rate**: Percentage of legitimate code incorrectly flagged
- **Critical Security Gaps**: Number of dangerous patterns that bypass validation
- **Overall Security Score**: Combined effectiveness rating

### Acceptable Thresholds
- ✅ **Excellent**: >95% malicious blocked, <5% false positives
- ✅ **Good**: >85% malicious blocked, <10% false positives  
- ⚠️ **Moderate**: >70% malicious blocked, <20% false positives
- ❌ **Poor**: <70% malicious blocked or >20% false positives

## 🛠 Usage Examples

### Running Quick Security Check
```bash
cd PhaserGame
python quick_security_test.py
```

### Running Comprehensive Tests
```bash
python security_test_runner.py --verbose --export-report detailed_report.html
```

### Testing via Web Interface
1. Start the Flask application: `python app.py`
2. Navigate to: `http://localhost:5000/security-test-ui`
3. Click "Run All Tests" to execute the full test suite

### Testing Custom Code
```python
from app import EnhancedSecurityValidator

validator = EnhancedSecurityValidator()
result = validator.validate('eval("alert(\\"XSS\\")")')

if result['is_safe']:
    print("Code is safe to execute")
else:
    print(f"Security violations: {result['violations']}")
```

### API Testing
```bash
curl -X POST http://localhost:5000/security-test \
  -H "Content-Type: application/json" \
  -d '{"code": "eval(\"alert(\\\"XSS\\\")\")", "test_name": "Custom Test"}'
```

## 🔧 Configuration

### Adjusting Security Thresholds
Edit `app.py` to modify validation parameters:

```python
class EnhancedSecurityValidator:
    def __init__(self):
        self.max_code_size = 50000          # Maximum code size in bytes
        self.max_string_concats = 15        # Maximum string concatenations
        self.max_entropy = 4.5              # Entropy threshold for obfuscation
```

### Adding New Attack Patterns
Add patterns to the `critical_patterns` list:

```python
self.critical_patterns = [
    r'new_dangerous_pattern',  # Add your pattern here
    # ... existing patterns
]
```

### Customizing Client-Side Validation
Modify `static/js/secure-executor.js`:

```javascript
this.bannedPatterns = [
    {
        pattern: /your_pattern_here/gi,
        message: "Description of the threat",
        severity: "CRITICAL"
    }
];
```

## 🚀 Integration with CI/CD

Add security testing to your build pipeline:

```yaml
# .github/workflows/security-test.yml
name: Security Tests
on: [push, pull_request]
jobs:
  security-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run security tests
        run: python security_test_runner.py --json
```

## 📈 Performance Considerations

- **Validation Speed**: ~1-5ms per code sample
- **Memory Usage**: ~10MB for comprehensive test suite
- **Concurrent Testing**: Thread-safe for parallel execution
- **Caching**: Results can be cached by code hash for repeated tests

## 🔍 Troubleshooting

### Common Issues

1. **ImportError for EnhancedSecurityValidator**
   - Ensure you're running from the PhaserGame directory
   - Check that `app.py` contains the validator class

2. **False Positives on Legitimate Code**
   - Review the pattern matching rules
   - Add exceptions for legitimate use cases
   - Consider lowering sensitivity thresholds

3. **Security Gaps Detected**
   - Analyze the specific attack vectors that bypass validation
   - Add new patterns to catch similar attacks
   - Consider implementing additional validation layers

4. **High Entropy False Positives**
   - Legitimate code with random IDs may trigger entropy checks
   - Adjust the entropy threshold or add context-aware analysis

## 📚 Additional Resources

- [OWASP Code Injection Prevention](https://owasp.org/www-community/attacks/Code_Injection)
- [JavaScript Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [Phaser.js Security Guidelines](https://phaser.io/tutorials/getting-started-phaser3)

## 🤝 Contributing

To add new security tests:

1. Add test cases to the appropriate test file
2. Update the validation patterns if needed
3. Run the full test suite to ensure no regressions
4. Update documentation with new attack vectors

## 📊 Current Test Coverage

- **Total Test Cases**: 50+
- **Attack Categories**: 10
- **Malicious Patterns**: 40+
- **Legitimate Patterns**: 15+
- **Execution Environments**: Client + Server
- **Output Formats**: Console, JSON, HTML, Web UI

This comprehensive security testing system ensures that your game development platform remains secure while providing a smooth development experience for legitimate users.
