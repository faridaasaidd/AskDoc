import re
from typing import Tuple

class InputGuardrail:
    """Input Guardrail: Validates user input before reaching the LLM across all major safety categories."""
    
    MAX_INPUT_LENGTH = 2000
    
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous\s+)?instructions",
        r"system\s+prompt\s+override",
        r"you\s+are\s+now\s+dan",
        r"do\s+anything\s+now",
        r"jailbreak",
        r"forget\s+(all\s+)?(previous|prior)\s+rules",
        r"bypass\s+(safety|filter|security|firewall|password|auth|rules)",
        r"developer\s+mode\s+enabled",
        r"act\s+as\s+an?\s+(unrestricted|uncensored|malicious)",
        r"pretend\s+(you\s+have\s+)?no\s+(restrictions|safety|rules)",
    ]

    SELF_HARM_PATTERNS = [
        r"\bkill\s+my\s*self\b",
        r"\bsuicide\b",
        r"\bend\s+my\s+life\b",
        r"\bcut\s+my\s*self\b",
        r"\bwant\s+to\s+die\b",
        r"\boverdose\s+(on|my\s*self)\b",
        r"\bhow\s+to\s+(commit\s+)?suicide\b",
        r"\bhow\s+to\s+die\b",
        r"\bself\s*harm\b",
        r"\bhang\s+my\s*self\b",
    ]

    VIOLENCE_HARMFUL_PATTERNS = [
        r"\bhow\s+to\s+(kill|murder|stab|shoot|poison|strangle|suffocate|decapitate|assassinate|hurt|harm)\b",
        r"\b(kill|murder|stab|shoot|poison|strangle|suffocate|decapitate|assassinate|hurt|harm)\s+(someone|somebody|a\s+person|people|others|anyone|him|her|them|my\s+\w+|boss|coworker|enemy)\b",
        r"\bhow\s+(can|do)\s+i\s+(kill|murder|stab|shoot|poison|harm|assassinate|hurt)\b",
        r"\b(ways|instructions|steps|guide|methods)\s+(to|for)\s+(kill|murder|stab|shoot|poison|harm|assassinate|hurt)\b",
        r"\bhow\s+to\s+(hurt|injure|beat|torture|kidnap|abduct)\s+(someone|somebody|a\s+person|people|others|my\s+\w+|boss|coworker)\b",
        r"\b(inflict|cause)\s+(physical\s+)?harm\s+on\s+(someone|others|a\s+person|people|my\s+\w+|boss|coworker)\b",
        r"\bneutralize\s+(someone|somebody|enemy|others|a\s+person|people)\b",
        r"\bhow\s+to\s+run\s+over\b",
        r"\brun\s+over\s+(someone|somebody|a\s+person|people|others)\b",
        r"\bphysical\s+(assault|battery)\s+instructions\b",
    ]

    WEAPONS_EXPLOSIVES_PATTERNS = [
        r"\bhow\s+to\s+(make|build|create|construct|manufacture)\s+(a\s+)?(bomb|explosive|weapon|gun|knife|firearm|molotov|pipe\s*bomb|dirty\s*bomb|landmine|c4)\b",
        r"\b(make|build|create|construct|manufacture)\s+(a\s+)?(bomb|explosive|weapon|gun|knife|firearm|molotov|pipe\s*bomb|dirty\s*bomb|landmine|c4)\b",
        r"\bhow\s+to\s+(make|synthesize|manufacture)\s+(poison|nerve\s+agent|cyanide|ricin|anthrax|mustard\s+gas)\b",
        r"\b(chemical|biological|radiological|nuclear)\s+weapon\b",
        r"\bhow\s+to\s+(convert|modify)\s+(a\s+)?(gun|firearm)\s+to\s+automatic\b",
        r"\bhow\s+to\s+3d\s*print\s+a\s+(gun|firearm|weapon)\b",
    ]

    CYBERATTACK_MALWARE_PATTERNS = [
        r"\bhow\s+to\s+(build|create|write|deploy|generate)\s+(malware|ransomware|virus|trojan|keylogger|spyware|rootkit)\b",
        r"\bhow\s+to\s+(hack|crack|breach)\b",
        r"\bhow\s+to\s+launch\s+(a\s+)?(ddos|denial\s+of\s+service)\b",
        r"\b(steal|bypass)\s+(passwords?|credentials?|session\s+cookies?|security|firewall)\b",
        r"\bgenerate\s+(a\s+)?phishing\s+(email|site|template)\b",
    ]

    CRIMINAL_ILLEGAL_PATTERNS = [
        r"\bhow\s+to\s+(rob|burglarize|steal\s+from)\s+(a\s+)?(bank|store|house|person)\b",
        r"\bhow\s+to\s+counterfeit\s+(money|currency|passports?|documents?)\b",
        r"\bhow\s+to\s+commit\s+(arson|fraud|theft|burglary|robbery|identity\s+theft|credit\s+card\s+fraud|tax\s+evasion|insurance\s+fraud)\b",
        r"\bhow\s+to\s+launder\s+money\b",
        r"\bhow\s+to\s+(shoplift|carjack)\b",
    ]

    DRUGS_CHEMICALS_PATTERNS = [
        r"\bhow\s+to\s+(make|cook|synthesize|manufacture)\s+(meth|methamphetamine|fentanyl|heroin|cocaine|lsd|mdma|ecstasy)\b",
        r"\brecipe\s+for\s+(cooking\s+meth|synthesizing\s+fentanyl)\b",
        r"\bhow\s+to\s+synthesize\b.*\b(illicit\s+drugs?|narcotics?)\b",
    ]

    HARASSMENT_DOXXING_PATTERNS = [
        r"\bhow\s+to\s+doxx?\s+(someone|somebody|a\s+person)\b",
        r"\bhow\s+to\s+(harass|stalk)\s+(someone|somebody|a\s+person)\b",
        r"\b(how\s+to\s+)?(express|promote|spread|use)\s+hate\s+speech\b",
    ]

    def __init__(self):
        self.injection_patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self.self_harm_patterns = [re.compile(p, re.IGNORECASE) for p in self.SELF_HARM_PATTERNS]
        
        self.harmful_categories = [
            ("violence", [re.compile(p, re.IGNORECASE) for p in self.VIOLENCE_HARMFUL_PATTERNS]),
            ("weapons", [re.compile(p, re.IGNORECASE) for p in self.WEAPONS_EXPLOSIVES_PATTERNS]),
            ("cyber", [re.compile(p, re.IGNORECASE) for p in self.CYBERATTACK_MALWARE_PATTERNS]),
            ("crime", [re.compile(p, re.IGNORECASE) for p in self.CRIMINAL_ILLEGAL_PATTERNS]),
            ("drugs", [re.compile(p, re.IGNORECASE) for p in self.DRUGS_CHEMICALS_PATTERNS]),
            ("harassment", [re.compile(p, re.IGNORECASE) for p in self.HARASSMENT_DOXXING_PATTERNS]),
        ]

    def check(self, user_input: str) -> Tuple[bool, str]:
        if not user_input or not user_input.strip():
            return False, "Input question cannot be empty."

        if len(user_input) > self.MAX_INPUT_LENGTH:
            return False, f"Question exceeds maximum allowed length of {self.MAX_INPUT_LENGTH} characters."
            
        for pattern in self.injection_patterns:
            if pattern.search(user_input):
                return False, "I cannot process this request due to safety guardrail policies regarding prompt injection attempts."

        for pattern in self.self_harm_patterns:
            if pattern.search(user_input):
                return False, (
                    "If you or someone you know is in crisis or distress, please reach out for immediate support. "
                    "You can call or text the Suicide & Crisis Lifeline at 988 (in the US/Canada), or contact emergency services (911/112/999). "
                    "Help is available 24/7."
                )

        for category_name, patterns in self.harmful_categories:
            for pattern in patterns:
                if pattern.search(user_input):
                    return False, "I cannot assist with requests involving violence, physical harm, illegal acts, or dangerous activities."

        return True, ""


class PIIDetector:
    
    PATTERNS = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "PHONE": r"\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    }

    def redact(self, text: str) -> str:
        if not text:
            return text
            
        redacted = text
        for pii_type, pattern in self.PATTERNS.items():
            redacted = re.sub(pattern, f"[REDACTED_{pii_type}]", redacted)
            
        return redacted


class SafetyLayer:
    """Combined input/output guardrails + PII handling."""
    
    def __init__(self):
        self.input_guard = InputGuardrail()
        self.pii = PIIDetector()

    def check_input(self, text: str) -> Tuple[bool, str]:
        return self.input_guard.check(text)

    def sanitize_output(self, text: str) -> str:
        return self.pii.redact(text)


_safety_layer = SafetyLayer()

def sanitize_and_validate_input(text: str) -> Tuple[bool, str]:
    return _safety_layer.check_input(text)

def redact_pii(text: str) -> str:
    return _safety_layer.sanitize_output(text)

