import os
import json
from rainsweep.history import HistoryManager


def test_history_manager_shared_rules(tmp_path):
    # Create a temporary domain_rules.json
    rules_content = {"hatenablog.com": "default"}
    rules_file = tmp_path / "domain_rules.json"
    rules_file.write_text(json.dumps(rules_content))

    # Mock the directory where history.py looks for rules
    import rainsweep.history

    # Instead, we can manually set the rules_file after init or mock it.
    # For simplicity, let's just test the logic by providing a custom history file.
    history_file = tmp_path / "warnings_history.json"
    hm = HistoryManager(history_file=str(history_file))
    
    # Manually inject shared rules for testing
    hm.shared_rules = {"hatenablog.com": "default"}
    
    assert hm.get_preferred_ua("https://example.hatenablog.com/entry/1") == "default"
    assert hm.get_preferred_ua("https://other.com") is None


def test_history_manager_learning(tmp_path):
    history_file = tmp_path / "warnings_history.json"
    hm = HistoryManager(history_file=str(history_file))
    
    url = "https://learned-domain.com/path"
    hm.update_domain_rule(url, "browser")
    assert hm.get_preferred_ua(url) == "browser"
    
    hm.save()
    assert os.path.exists(history_file)
    
    # Load again
    hm2 = HistoryManager(history_file=str(history_file))
    assert hm2.get_preferred_ua(url) == "browser"


def test_history_manager_subdomain_matching(tmp_path):
    hm = HistoryManager(history_file=str(tmp_path / "history.json"))
    hm.shared_rules = {"hatena.ne.jp": "default"}
    
    assert hm.get_preferred_ua("https://b.hatena.ne.jp/entry") == "default"
    assert hm.get_preferred_ua("https://hatena.ne.jp") == "default"
