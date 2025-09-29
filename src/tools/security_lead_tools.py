"""Travel Security Tools - Minimal Security Analysis"""

import re
from typing import Dict, List, Any


def get_security_tools():
    """Get essential security tools"""
    return [
        SecurityScanner(),
        SecretDetector(),
        TravelSecurityChecker()
    ]


class SecurityScanner:
    """Basic security scanner"""
    name = "security_scan"
    
    async def scan(self, code: str) -> Dict[str, Any]:
        """Run security scan"""
        issues = []
        
        # Check secrets
        if any(x in code.lower() for x in ['password=', 'api_key=', 'token=']):
            issues.append("Hardcoded credentials found")
        
        # Check HTTP usage
        if 'http://' in code and any(api in code.lower() for api in ['amadeus', 'omio']):
            issues.append("Insecure API calls detected")
        
        # Check input validation
        if 'request.' in code.lower() and 'validate' not in code.lower():
            issues.append("Missing input validation")
        
        return {
            'status': 'success',
            'issues': issues,
            'score': max(0, 100 - len(issues) * 25)
        }


class SecretDetector:
    """Detect hardcoded secrets"""
    name = "detect_secrets"
    
    def scan(self, content: str) -> Dict[str, Any]:
        """Scan for secrets"""
        patterns = [
            r'api[_-]?key\s*[=:]\s*["\'][^"\']{15,}["\']',
            r'password\s*[=:]\s*["\'][^"\']{8,}["\']',
            r'token\s*[=:]\s*["\'][^"\']{20,}["\']'
        ]
        
        secrets = []
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if not any(test in match.group().lower() for test in ['test', 'example']):
                    secrets.append({
                        'type': 'credential',
                        'line': content[:match.start()].count('\n') + 1,
                        'severity': 'HIGH'
                    })
        
        return {
            'secrets': secrets,
            'count': len(secrets),
            'recommendations': ['Use environment variables'] if secrets else []
        }


class TravelSecurityChecker:
    """Travel-specific security checks"""
    name = "travel_security"
    
    def check(self, code: str) -> Dict[str, Any]:
        """Check travel security"""
        issues = []
        
        # Travel API checks
        travel_apis = ['amadeus', 'omio', 'booking']
        if any(api in code.lower() for api in travel_apis):
            if 'http://' in code:
                issues.append("Travel API using HTTP")
            if 'try:' not in code:
                issues.append("Missing error handling")
        
        # Payment security
        payment_terms = ['payment', 'credit_card']
        if any(term in code.lower() for term in payment_terms):
            if 'encrypt' not in code.lower():
                issues.append("Payment data not encrypted")
        
        return {
            'issues': issues,
            'travel_score': max(0, 100 - len(issues) * 30),
            'recommendations': [
                'Use HTTPS for APIs',
                'Add error handling',
                'Encrypt payment data'
            ] if issues else []
        }
