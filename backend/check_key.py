import os
import google.generativeai as genai
from dotenv import load_dotenv

def check_api_key():
    """
    Safely loads the Google API key from the .env file and tests it
    by attempting to connect to the Google AI service.
    """
    print("--- Starting API Key Check ---")
    
    # Load environment variables from the .env file in the parent directory
    # This assumes you run the script from the 'backend' folder.
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        print("\n❌ ERROR: GOOGLE_API_KEY not found in the .env file.")
        print("Please make sure your .env file is in the project's root directory and contains the key.")
        return

    print("✅ API Key found in .env file.")
    
    try:
        # Configure the generative AI client with the key
        genai.configure(api_key=api_key)
        
        print("... Attempting to connect to Google AI services...")
        
        # A simple, lightweight call to list models to verify the key
        models = genai.list_models()
        
        # Check if we got a valid response
        if any('generateContent' in m.supported_generation_methods for m in models):
            print("\n✅ SUCCESS! Your API key is valid and connected successfully.")
            print("You can see available models like 'gemini-1.0-pro' in the list.")
        else:
            print("\n❌ ERROR: The API key is valid, but no usable models were found.")
            print("Please check your Google Cloud project permissions for the 'Generative Language API'.")

    except Exception as e:
        # This will catch authentication errors, network problems, etc.
        print(f"\n❌ FAILED: An error occurred during the connection test.")
        print(f"   Error Details: {e}")
        print("\n   Common reasons for failure include:")
        print("   1. The API key is incorrect or has been revoked.")
        print("   2. The 'Generative Language API' is not enabled in your Google Cloud project.")
        print("   3. A network issue is preventing connection to Google's servers.")

    print("\n--- API Key Check Finished ---")

if __name__ == "__main__":
    check_api_key()

### How to Use This Script
 
    
