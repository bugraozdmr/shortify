import requests
api_key = "sk_afc179c10dfbf7d0d32eceb627d0744778ddf1848fc4ae43"
url = "https://api.elevenlabs.io/v1/voices"
headers = {"Accept": "application/json", "xi-api-key": api_key}
response = requests.get(url, headers=headers)
print(response.status_code)
print(response.text[:500])
