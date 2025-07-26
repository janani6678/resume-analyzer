import google.generativeai as genai

# Replace with your Gemini API key
genai.configure(api_key="AIzaSyBpyN4E2UYQc2O6R1mrG1batGhgB3Wo2aU")

# List all available models and what methods they support
for model in genai.list_models():
    print(f"Model: {model.name}")
    print(f"Supported Methods: {model.supported_generation_methods}")
    print("---------------")
