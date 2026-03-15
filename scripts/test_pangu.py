import requests
import json

# 1. PASTE YOUR DETAILS HERE
TOKEN = "PMIIPbQYJKoZIhvcNAQcCoIIPXjCCD1oCAQExDTALBglghkgBZQMEAgEwgg1-BgkqhkiG9w0BBwGggg1wBIINbHsidG9rZW4iOnsiZXhwaXJlc19hdCI6IjIwMjYtMDItMjhUMTI6NTA6NTcuNTczMDAwWiIsInNpZ25hdHVyZSI6IkVBNWhjQzF6YjNWMGFHVmhjM1F0TVFBQUFBQUFBQVJaS3FsTlRkUDdPWEZQc1kwUmpVVWpIWGpsNVhtWVJLR0xaN2Y1VUxmNUZ4T1hUaVBnRkFoUW41bnBtTkdRQnNMcnIyUExmc1p1R0Zsc2lmejJyUVgzS29QMlZnbUZGWVlrWW1OdDhZSGJkbmJvQk9JMFFScjhYeWw0eXpib0Z1djlYdG56RUVYb1cvaXpNOTVpZUs0U25tZzY0am1BQzdCSzE2OTdPUXZvbXBGMm9GdWQvQlNRcWhBenNUZHpkOVo3cUUxcjhDbjdTZlkyaWFMSDdzQnRLNzR2UnJmaXpXTHNaTDNMamR6NUlrUUVXYVYwRjN0ckN2aFEzRU52NzN3eDVJNk95YUVrTHV0U2VoczVscnRyWTBER3IxUzdMYmFLQzZLSi9qQ2p6SjhhSnNtd05zM3cwRURnVVlpNkg5UVBCT2haZGhIUTFhWGkybkc1SDdzcU1BPT0iLCJtZXRob2RzIjpbInBhc3N3b3JkIl0sImNhdGFsb2ciOltdLCJyb2xlcyI6W3sibmFtZSI6Im9wX2dhdGVkX2NzYnNfcmVwX2FjY2VsZXJhdGlvbiIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19kaXNrQWNjIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZHNzX21vbnRoIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfb2JzX2RlZXBfYXJjaGl2ZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfY24tc291dGgtNGMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9kZWNfbW9udGhfdXNlciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nicl9zZWxsb3V0IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX29sZF9yZW91cmNlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX1JveWFsdHkiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF93ZWxpbmticmlkZ2VfZW5kcG9pbnRfYnV5IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY2JyX2ZpbGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9kbXMtcm9ja2V0bXE1LWJhc2ljIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX0VTaW5nbGVfY29weVNTRCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rtcy1rYWZrYTMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9vYnNfZGVjX21vbnRoIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY3Nic19yZXN0b3JlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY2JyX3Ztd2FyZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2lkbWVfbWJtX2ZvdW5kYXRpb24iLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9tdWx0aV9iaW5kIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX3NzZF9lbnRyeSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Ntbl9jYWxsbm90aWZ5IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9hcC1zb3V0aGVhc3QtM2QiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Byb2dyZXNzYmFyIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY2VzX3Jlc291cmNlZ3JvdXBfdGFnIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX3JldHlwZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2tvb21hcCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rtcy1hbXFwLWJhc2ljIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX3Bvb2xfY2EiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLXNvdXRod2VzdC0yYiIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h3Y3BoIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX29mZmxpbmVfZGlza180IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX3dlbGlua3JlZCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h2X3ZlbmRvciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfY24tbm9ydGgtNGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLW5vcnRoLTRkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2hlY3NfeCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nicl9maWxlc19iYWNrdXAiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfYWM3IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXBzIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY3Nic19yZXN0b3JlX2FsbCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfY24tbm9ydGgtNGYiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9vcF9nYXRlZF9yb3VuZHRhYmxlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX2V4dCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Bmc19kZWVwX2FyY2hpdmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2FwLXNvdXRoZWFzdC0xZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfcnUtbW9zY293LTFiIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9hcC1zb3V0aGVhc3QtMWQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hcHBzdGFnZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTFmIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX2FwcGxpY2F0aW9uIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX2NvbGQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfZ3B1X2c1ciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29wX2dhdGVkX21lc3NhZ2VvdmVyNWciLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfcmkiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF91bnZlcmlmaWVkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9ydS1ub3J0aHdlc3QtMmMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9pZWZfcGxhdGludW0iLCJpZCI6IjAifV0sInByb2plY3QiOnsiZG9tYWluIjp7Inhkb21haW5fdHlwZSI6IkhXQ19ISyIsIm5hbWUiOiJoaWRfLXB0aWl3ZmJ0NTVtbWF4IiwiaWQiOiJiZDcyNGYxYzBkYWQ0NTVmYTg5NTVlODY3YjIwZmE2YSIsInhkb21haW5faWQiOiIzMDAyNzAwMDAyOTIwODI2MyJ9LCJuYW1lIjoiYXAtc291dGhlYXN0LTEiLCJpZCI6IjI0OGU3ODNiN2Q2ZTRlYzE5Yjg5ZjJjYWRmOWY2M2EwIn0sImlzc3VlZF9hdCI6IjIwMjYtMDItMjdUMTI6NTA6NTcuNTczMDAwWiIsInVzZXIiOnsiZG9tYWluIjp7Inhkb21haW5fdHlwZSI6IkhXQ19ISyIsIm5hbWUiOiJoaWRfLXB0aWl3ZmJ0NTVtbWF4IiwiaWQiOiJiZDcyNGYxYzBkYWQ0NTVmYTg5NTVlODY3YjIwZmE2YSIsInhkb21haW5faWQiOiIzMDAyNzAwMDAyOTIwODI2MyJ9LCJuYW1lIjoia2Ftb19pYW0iLCJwYXNzd29yZF9leHBpcmVzX2F0IjoiIiwiaWQiOiJlMmIyMzUxMWI4YTk0ZWUwOGY1OTQ0YWZiMmM0NDZiZSJ9fX0xggHBMIIBvQIBATCBlzCBiTELMAkGA1UEBhMCQ04xEjAQBgNVBAgMCUd1YW5nRG9uZzERMA8GA1UEBwwIU2hlblpoZW4xLjAsBgNVBAoMJUh1YXdlaSBTb2Z0d2FyZSBUZWNobm9sb2dpZXMgQ28uLCBMdGQxDjAMBgNVBAsMBUNsb3VkMRMwEQYDVQQDDApjYS5pYW0ucGtpAgkA3LMrXRBhahAwCwYJYIZIAWUDBAIBMA0GCSqGSIb3DQEBAQUABIIBAF1atmdEV96OuTf8TpbInp30-lDheHFZW7nFssoJYklvnfIlRsZBjEm1hQqc7lH4OKCzfDMfuaK92SM6zs9Wuvbh-8aTzPpzeyiX23xPn1-9umKHTa3JgEeTWZU2VpzNeUvZEjy4ImQoyJqE4-GLBK1jEH7PRHTg8hTydtdRYPWKt7KaZeF1kvO4i3M4nGqqRcz-kJthudVKUzbdtocE4DGd4Uc7cac4rwaVuds-d7hwEBQtN1GDPl2XCGjCHv0s9j62ahayKtl2F-FU87ZrHyoFrTy6GUxlruk59UvUXAXBYGC4c-uPN-U4PfHXnNyZmX2bQ+6uK1EL2Vfk7bAjFzo="

PROJECT_ID = "248e783b7d6e4ec19b89f2cadf9f63a0"

# 2. THE ENDPOINT
# Note: Ensure this matches the region you deployed in (af-south-1 is Joburg)
URL = f"https://pangu.af-ap-south-1.myhuaweicloud.com/v1/{PROJECT_ID}/deployments/pangu-ai-nlp-v1/completions"

# 3. THE PAYLOAD (Asking Biz-Bantu a simple question)
headers = {
    "Content-Type": "application/json",
    "X-Auth-Token": TOKEN  # Your X-Subject-Token goes here
}

data = {
    "prompt": "You are Biz-Bantu. Briefly explain why keeping a digital record of sales is good for a Spaza shop.",
    "max_tokens": 150,
    "temperature": 0.7
}

def verify_access():
    print(f"📡 Sending request to Pangu (Project: {PROJECT_ID})...")
    
    try:
        # We use a timeout because your laptop had connection issues before
        response = requests.post(URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Your token is working.")
            result = response.json()
            print("\n--- Pangu Response ---")
            # The structure might vary slightly based on your specific Pangu version
            print(json.dumps(result, indent=2))
            print("----------------------")
        
        elif response.status_code == 401:
            print("❌ ERROR: Token is invalid or has expired (they only last 24 hours).")
        
        elif response.status_code == 403:
            print("❌ ERROR: Permissions issue. Check if your IAM user has 'ModelArts FullAccess'.")
            
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")

    except Exception as e:
        print(f"⚠️ CONNECTION FAILED: {str(e)}")
        print("\nPossible fix: Check your internet or verify the 'af-south-1' endpoint is correct for your region.")

if __name__ == "__main__":
    verify_access()