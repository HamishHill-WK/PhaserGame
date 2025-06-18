print("Starting security validator test...")

try:
    from app import EnhancedSecurityValidator
    print("✅ Successfully imported EnhancedSecurityValidator")
    
    validator = EnhancedSecurityValidator()
    print("✅ Successfully created validator instance")
    
    # Test malicious code
    result = validator.validate('eval("alert")')
    print(f"🚨 Malicious code test - Safe: {result['is_safe']}")
    print(f"   Violations: {result['violations']}")
    
    # Test benign code
    result2 = validator.validate('function test() { return 42; }')
    print(f"✅ Benign code test - Safe: {result2['is_safe']}")
    print(f"   Violations: {result2['violations']}")
    
    print("Security validator test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
