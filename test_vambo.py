import requests
import json

def test_vambo_api():
    # API Configuration
    api_key = ""
    identify_url = "https://api.vambo.ai/v1/identify/text"
    translate_url = "https://api.vambo.ai/v1/translate/text"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test 1: Language Identification
    print("\n=== Testing Language Identification ===")
    identify_payload = {
        "text": "Hello, how are you?"
    }
    
    try:
        print(f"\nIdentifying text: {identify_payload['text']}")
        response = requests.post(
            identify_url,
            headers=headers,
            json=identify_payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Translation with corrected parameter names
    print("\n=== Testing Translation ===")
    translation_tests = [
        {
            "text": "Welcome! Please select your language and ask a question about menstruation, puberty, or general health.",
            "source_lang": "eng",
            "target_lang": "swh"
        },
        {
            "text": "How are you?",
            "source_lang": "eng",
            "target_lang": "nya"
        },
        {
            "text": "Goodnight sleepyhead",
            "source_lang": "eng",
            "target_lang": "zul"
        }
    ]

    for test in translation_tests:
        try:
            print(f"\nTranslating: {json.dumps(test, indent=2)}")
            response = requests.post(
                translate_url,
                headers=headers,
                json=test
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_vambo_api()
