import json
import os
from urllib.parse import urlparse


class HistoryManager:
    """Manages domain rules and learning from past results."""

    def __init__(self, history_file: str = "warnings_history.json"):
        self.history_file = history_file
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.rules_file = os.path.join(self.base_dir, "domain_rules.json")

        # Load shared rules
        self.shared_rules = {}
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, "r") as f:
                    self.shared_rules = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Load local history/rules
        self.history = {"domain_rules": {}}
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        if "domain_rules" not in self.history:
            self.history["domain_rules"] = {}

    def get_preferred_ua(self, url: str) -> str | None:
        """Extract domain and check if we have a preferred UA type."""
        domain = self._extract_domain(url)
        if not domain:
            return None

        # Check local rules first (learned)
        if domain in self.history["domain_rules"]:
            return self.history["domain_rules"][domain]

        # Check shared rules
        if domain in self.shared_rules:
            return self.shared_rules[domain]

        # Check subdomains if it's hatena
        for rule_domain, ua_type in self.shared_rules.items():
            if domain.endswith("." + rule_domain):
                return ua_type

        return None

    def update_domain_rule(self, url: str, ua_type: str):
        """Update local rules with a worked UA type."""
        domain = self._extract_domain(url)
        if domain:
            self.history["domain_rules"][domain] = ua_type

    def save(self):
        """Save history to file."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""
