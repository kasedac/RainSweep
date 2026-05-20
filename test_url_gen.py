from unittest.mock import MagicMock
from raindropiopy.api import API
api = API(token="dummy")
api.session = MagicMock()
try:
    api.put("test/path", json={"key": "value"})
except:
    pass
# Check all methods on session
for call in api.session.mock_calls:
    print(f"Call: {call}")
