import re
import esprima  

class SimpleSecurityValidator:
    def __init__(self):
        self.critical_patterns = [
            r'\beval\s*\(',
            r'\bnew\s+Function\s*\(',
            r'\bsetTimeout\s*\(\s*[\'"`]',
            r'\bsetInterval\s*\(\s*[\'"`]',
            r'window\s*\[\s*[\'"`]eval[\'"`]\s*\]',
            r'globalThis\s*\[\s*[\'"`]eval[\'"`]\s*\]',
            r'document\s*\.\s*write\s*\(',
            r'innerHTML\s*=',
            r'outerHTML\s*=',
            r'insertAdjacentHTML\s*\(',
            r'fetch\s*\(',
            r'XMLHttpRequest',
            r'WebSocket\s*\(',
            r'Object\s*\.\s*prototype',
            r'__proto__\s*=',
            r'constructor\s*\.\s*prototype',
            r'import\s*\(',
            r'require\s*\(',
            r'process\s*\.',
            r'global\s*\.',
            r'Buffer\s*\.'
        ]
    
    def validate(self, code):
        violations = []
        
        # 1. Basic pattern matching (fast, reliable)
        for pattern in self.critical_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(f"Dangerous pattern detected: {pattern}")
        
        # 2. AST parsing (this actually works with esprima)
        try:
            ast = esprima.parseScript(code)
            ast_violations = self._check_ast(ast)
            violations.extend(ast_violations)
        except Exception as e:
            violations.append(f"Code parsing failed: {str(e)}")
        
        return {
            'is_safe': len(violations) == 0,
            'violations': violations
        }
    
    def _check_ast(self, ast):
        # Simple AST traversal that actually works
        violations = []
        
        def traverse(node):
            if isinstance(node, dict):
                if node.get('type') == 'CallExpression':
                    callee = node.get('callee', {})
                    if (callee.get('type') == 'Identifier' and 
                        callee.get('name') in ['eval', 'Function']):
                        violations.append(f"Dangerous function call: {callee.get('name')}")
                
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        traverse(value)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        
        traverse(ast)
        return violations
