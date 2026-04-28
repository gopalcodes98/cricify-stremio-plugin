import requests
import uuid
import config

PACKAGE_NAME = "com.cricfy.tv"

def fetch_remote_config():
    if not config.CRICFY_FIREBASE_API_KEY or not config.CRICFY_FIREBASE_APP_ID or not config.CRICFY_FIREBASE_PROJECT_NUMBER:
        print("Warning: Firebase config not set.")
        return None

    try:
        url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{config.CRICFY_FIREBASE_PROJECT_NUMBER}/namespaces/firebase:fetch"
        app_instance_id = uuid.uuid4().hex

        payload = {
            "appInstanceId": app_instance_id,
            "appInstanceIdToken": "",
            "appId": config.CRICFY_FIREBASE_APP_ID,
            "countryCode": "US",
            "languageCode": "en-US",
            "platformVersion": "30",
            "timeZone": "UTC",
            "appVersion": "5.0",
            "appBuild": "50",
            "packageName": PACKAGE_NAME,
            "sdkVersion": "22.1.0",
            "analyticsUserProperties": {}
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Android-Package": PACKAGE_NAME,
            "X-Goog-Api-Key": config.CRICFY_FIREBASE_API_KEY,
            "X-Google-GFE-Can-Retry": "yes"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("entries", {})
    except Exception as e:
        print(f"Error fetching remote config: {e}")
        return None

def get_provider_api_url():
    """
    Gets the provider API URL from Firebase Remote Config.
    Uses cric_api2 as secondary endpoint, or cric_api1.
    """
    entries = fetch_remote_config()
    if not entries:
        return "https://cfyhljddgbkkufh82.top" # Fallback from Kotlin LiveEventsProvider.kt
    return entries.get("cric_api2") or entries.get("cric_api1") or "https://cfyhljddgbkkufh82.top"

