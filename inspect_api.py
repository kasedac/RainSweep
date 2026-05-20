import os
from raindropiopy.api import API
token = os.environ.get("RAINDROP_TOKEN", "fake")
api = API(token=token)
print(f"API methods: {[m for m in dir(api) if not m.startswith('_')]}")
if hasattr(api, 'baseUrl'):
    print(f"Base URL: {api.baseUrl}")
elif hasattr(api, 'base_url'):
    print(f"Base URL: {api.base_url}")
