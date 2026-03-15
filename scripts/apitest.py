# import requests

# # Replace these with the details from the MaaS page
# API_KEY = "TgwYhhkuRmMvrUL8gtYX_sKxhWoFqLHI9bXEf94f-X72pdTmcIsT1RZ0bueMYHeBNRkkhOt9k5cN6KOLwfwOxQ"
# URL = "https://api-ap-southeast-1.modelarts-maas.com/v1/chat/completions"

# headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {API_KEY}"
# }

# payload = {
#     "model": "qwen3-8b",
#     "messages": [
#         {"role": "user", "content": "Sawubona! Can you help my township business?"}
#     ]
# }

# response = requests.post(URL, headers=headers, json=payload)
# print(response.json()['choices'][0]['message']['content'])

# import requests
# import json

# # 1. YOUR SETTINGS
# OPENROUTER_API_KEY = "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"

# # Exact ID for the model you found
# MODEL_ID = "qwen/qwen3-coder:free" 

# def call_biz_bantu(message):
#     url = "https://openrouter.ai/api/v1/chat/completions"
    
#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json",
#         "HTTP-Referer": "http://localhost:3000", # Can be any URL for your dev environment
#         "X-Title": "Biz-Bantu-Advisor"
#     }

#     # 2. THE PERSONA (Tailored for Qwen3's reasoning)
#     payload = {
#         "model": MODEL_ID,
#         "messages": [
#             {
#                 "role": "system", 
#                 "content": (
#                     "You are Biz-Bantu, a sophisticated but accessible business advisor for South African entrepreneurs. "
#                     "You specialize in township economies (Spaza shops, car washes, street vendors). "
#                     "You use local context like 'kasi', 'shisa nyama', and 'stokvel'. "
#                     "Respond in a friendly mix of English and the user's preferred local language (isiZulu/Sesotho)."
#                 )
#             },
#             {"role": "user", "content": message}
#         ],
#         "temperature": 0.5, # Lower = more professional/accurate business advice
#         "max_tokens": 800
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload)
        
#         if response.status_code == 200:
#             data = response.json()
#             return data['choices'][0]['message']['content']
#         else:
#             return f"Error {response.status_code}: {response.text}"
            
#     except Exception as e:
#         return f"Request failed: {str(e)}"

# # 3. TEST RUN
# if __name__ == "__main__":
#     test_query = "Ngidinga usizo nge-marketing yespaza sami. How do I get more customers?"
#     print("📢 Sending to Biz-Bantu (Qwen3 80B)...")
#     print("-" * 30)
#     print(call_biz_bantu(test_query))


    #####################################33
# import requests
# import json
# import time

# # 1. SETTINGS
# OPENROUTER_API_KEY = "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"


# # The "Smart List" - We try the smartest first, but have 3 backups
# MODELS_TO_TRY = [
#     "qwen/qwen-3-coder-480b-a35b:free",  # The Dream Model (Often busy)
#     "qwen/qwen-3-next-80b-instruct:free", # The Advisor (Often busy)
#     "qwen/qwen-2.5-72b-instruct:free",   # High reliability, very smart
#     "qwen/qwen-2.5-7b-instruct:free"     # The "Never-Fail" backup (Always works)
#     "qwen/qwen3-embedding-8b"
# ]

# def ask_biz_bantu_safe(user_input):
#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json",
#         "X-Title": "MzansiPulse_Demo"
#     }

#     for model in MODELS_TO_TRY:
#         print(f"🔄 Attempting {model}...")
        
#         payload = {
#             "model": model,
#             "messages": [
#                 {"role": "system", "content": "You are Biz-Bantu, a supportive South African business assistant."},
#                 {"role": "user", "content": user_input}
#             ]
#         }

#         try:
#             response = requests.post(url, headers=headers, json=payload)
            
#             if response.status_code == 200:
#                 print(f"✅ Success! Responded via {model}")
#                 return response.json()['choices'][0]['message']['content']
            
#             elif response.status_code == 429:
#                 print(f"⚠️ {model} is busy. Swapping to next model...")
#                 continue # Try the next model in the list
            
#             else:
#                 print(f"❌ {model} failed with error {response.status_code}")
#                 continue

#         except Exception as e:
#             print(f"📡 Connection error with {model}: {e}")
#             continue

#     return "System Overload: Even the backups are busy. Please try again in 10 seconds."

# # 2. TEST
# if __name__ == "__main__":
#     print(ask_biz_bantu_safe("How do I log a sale of R100 for a bucket of chicken?"))

    #####################33333333333#################3
import requests
import json

# 1. SETTINGS
OPENROUTER_API_KEY = "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"

# Since you have credits, use these high-performance IDs:
MODELS_TO_TRY = [
    "qwen/qwen3.5-flash-02-23",          # $0.40/1M - Fast, smart, knows 2026 context.
    "deepseek/deepseek-chat-v3.1",     # $0.28/1M - The global value champion.
    "google/gemini-2.0-flash-001", # $0.40/1M - Best for "Multimodal" (Voice/Images).
    "meta-llama/llama-3.3-70b-instruct" # $0.79/1M - Reliable if others fail.
]

def call_biz_bantu(user_query, extraction_mode=False):
    """
    Calls the AI models in sequence until one succeeds.
    extraction_mode: Set to True if you want raw JSON data back.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mzansipulse.io", # Required for 2026 routing
        "X-Title": "MzansiPulse-BizBantu"
    }

    # Dynamic System Prompt based on needs
    if extraction_mode:
        system_content = (
            "You are a JSON data extractor. Output ONLY valid JSON. "
            "Fields: {'item': str, 'amount': int, 'currency': 'ZAR', 'type': 'sale'|'expense'}"
        )
    else:
        system_content = (
            "You are Biz-Bantu, a street-smart business mentor for SA entrepreneurs. "
            "Use English, Zulu, and Sotho. Be warm and practical. "
            "If someone logs a sale, confirm it with a 'Halala mfowethu!'"
        )

    for model in MODELS_TO_TRY:
        print(f"🔄 Attempting {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.6 if not extraction_mode else 0.1 # Lower temp for data
        }

        try:
            # Short timeout so your app doesn't hang
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ Success via {model}!")
                return content
            
            elif response.status_code == 400:
                print(f"❌ {model} failed (Error 400: Check ID or Credits)")
            elif response.status_code == 429:
                print(f"❌ {model} is Rate Limited (Too many requests)")
            else:
                print(f"❌ {model} failed with status {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"⏰ {model} timed out. Skipping...")
        except Exception as e:
            print(f"📡 Connection error: {e}")

    return "Shu! All my brains are busy right now. Try again in a minute, my friend."

# --- 2. EXECUTION ---
if __name__ == "__main__":
    print("--- MZANSIPULSE API TESTER 2026 ---")
    
    # Test 1: Friendly Business Chat
    print("\n[TEST 1: CHAT]")
    user_input = "Sawubona Bantu! I just sold a bucket of chicken for R100."
    chat_reply = call_biz_bantu(user_input, extraction_mode=False)
    print(f"\nBIZ-BANTU: {chat_reply}")

    print("\n" + "-"*30)

    # Test 2: Data Extraction (For your Database)
    print("\n[TEST 2: DATA EXTRACTION]")
    data_reply = call_biz_bantu(user_input, extraction_mode=True)
    print(f"\nDATABASE JSON: {data_reply}")