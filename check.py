import google.generativeai as genai

# Methanata oyaage aluth API key eka danna
genai.configure(api_key="AIzaSyCCB-g1u3-6Jp_w9rksStGRoW8F8afKE3g")

print("Working models for this API key:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)