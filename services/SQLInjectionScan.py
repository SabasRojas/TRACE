from typing import List
import re

class SQLInjectionScan:
    SQL_PATTERNS = [
        r"(?i)(union.*select)",
        r"(?i)(select.*from.*where)",
        r"(?i)(insert\s+into.*values)",
        r"(?i)(drop\s+table)",
        r"(?i)(--|#|/\*|\*/|xp_)"
    ]

    COMMON_SQL_ERRORS = [
        "you have an error in your sql syntax",
        "unclosed quotation mark",
        "quoted string not properly terminated",
        "unexpected end of SQL command",
        "sql error",
        "fatal error",
        "syntax error at or near"
    ]
    
    SQL_PAYLOADS = [
        "' OR 1=1 --",
        "' UNION SELECT NULL, version(); --",
        "1' OR 1=1#",
        "1' AND 1=2#"
    ]
    
    SHORT_PARAMETER_LIST = [
        "id",
        "q",
    ]

    ADVANCED_SQL_PAYLOADS = [
        "' UNION SELECT * FROM *.tables --",
        "' UNION SELECT * FROM *.columns --",
        "' UNION SELECT null, version() --",
        "' OR EXISTS (SELECT * FROM users) --",
        "' AND (SELECT COUNT(*) FROM *.tables) > 0 --",
    ]

    @staticmethod
    def scan_input_sql_injection(response_text: str) -> bool:
        """Scan the server response for SQL injection signs."""
        for pattern in SQLInjectionScan.SQL_PATTERNS:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        for error_message in SQLInjectionScan.COMMON_SQL_ERRORS:
            if error_message.lower() in response_text.lower():
                return True
        return False

    @staticmethod
    def analyze_query(query: str) -> bool:
        """Scan a query for SQL injection patterns."""
        for pattern in SQLInjectionScan.SQL_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_sql_vulnerabilities(logs: List[str]) -> List[str]:
        suspicious_queries = [log for log in logs if SQLInjectionScan.analyze_query(log)]
        return suspicious_queries


    @staticmethod
    def process_response(response: str) -> str:
        if "error" in response.lower():
            return "Possible SQL Injection Error Detected"
        return "Response processed successfully"
    
    