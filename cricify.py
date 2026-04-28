import requests
from crypto import decrypt_data
from firebase import get_provider_api_url

def fetch_live_events():
    """Fetches list of live events/channels from the API"""
    base_url = get_provider_api_url()
    url = f"{base_url}/live_events.txt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            encrypted_data = response.text
            decrypted_data = decrypt_data(encrypted_data)
            if decrypted_data:
                import json
                return json.loads(decrypted_data)
        return []
    except Exception as e:
        print(f"Error fetching live events: {e}")
        return []

def fetch_channel_streams(slug):
    """Fetches stream URLs for a given channel slug."""
    base_url = get_provider_api_url()
    url = f"{base_url}/channels/{slug.lower()}.txt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            encrypted_data = response.text
            decrypted_data = decrypt_data(encrypted_data)
            if decrypted_data:
                import json
                return json.loads(decrypted_data)
        return None
    except Exception as e:
        print(f"Error fetching channel streams: {e}")
        return None

def parse_stream_link(link):
    """Parses stream link that may contain headers after |"""
    headers = {}
    if "|" not in link:
        return link, headers

    parts = link.split("|", 1)
    url = parts[0]
    
    if len(parts) > 1:
        header_part = parts[1]
        for header_pair in header_part.split("&"):
            key_value = header_pair.split("=", 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                val = key_value[1].strip()
                # Normalize header names
                lower_key = key.lower()
                if lower_key == "user-agent": key = "User-Agent"
                elif lower_key == "referer": key = "Referer"
                elif lower_key == "origin": key = "Origin"
                elif lower_key == "cookie": key = "Cookie"
                headers[key] = val

    return url, headers
