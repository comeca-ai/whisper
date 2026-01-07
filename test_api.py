"""
Test script for Whisper API
"""
import requests
import sys

def test_api(audio_file_path: str, api_url: str = "http://localhost:8000"):
    """Test the Whisper API with an audio file."""
    
    print(f"Testing Whisper API at {api_url}")
    
    # Test health check
    print("\n1. Testing health check...")
    response = requests.get(f"{api_url}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test models list
    print("\n2. Testing models list...")
    response = requests.get(f"{api_url}/models")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test transcription
    print(f"\n3. Testing transcription with file: {audio_file_path}")
    with open(audio_file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'model': 'base',
            'language': 'pt',  # Portuguese
            'task': 'transcribe'
        }
        response = requests.post(f"{api_url}/transcribe", files=files, data=data)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Transcribed text: {result['text']}")
        print(f"   Language: {result['language']}")
        print(f"   Number of segments: {len(result['segments'])}")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <audio_file_path>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    test_api(audio_file)
