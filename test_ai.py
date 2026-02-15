import google.generativeai as genai

# حط مفتاحك هنا
genai.configure(api_key="AIzaSyB0xTDwW71QdWdjOR2ykIWw5XwI9-SMWh8") 

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")