# """
# Pangu AI Helper - Production Ready
# Enhanced multilingual support with deep vernacular understanding
# Handles ANY question intelligently across all languages
# """
# from openrouter_helper import OpenRouterHelper
# import requests
# import json
# import os
# from datetime import datetime, timedelta

# class PanguAIHelper:
#     """
#     Helper class for Huawei Pangu AI API
#     Provides business advice in multiple South African languages
#     """
    
#     def __init__(self, project_id: str, access_key: str, secret_key: str, region: str = 'af-south-1'):
#         """Initialize Pangu AI connection"""
#         self.project_id = project_id
#         self.access_key = access_key
#         self.secret_key = secret_key
#         self.region = region
#         self.token = None
#         self.token_expires = None
        
#         # API endpoint
#         self.api_endpoint = f"https://pangu.{region}.myhuaweicloud.com/v1/{project_id}/infers"
        
#         # Initialize OpenRouter for real AI
#         self.openrouter = OpenRouterHelper()
        
#         print(f"🤖 Pangu AI Helper initialized for project: {project_id}")
    
#     # ════════════════════════════════════════════════════════════════════════
#     # IAM TOKEN GENERATION
#     # ════════════════════════════════════════════════════════════════════════
    
#     def get_iam_token(self):
#         """Get IAM X-Subject-Token"""
        
#         # OPTION 1: Use existing token if provided
#         USE_EXISTING_TOKEN = os.environ.get('USE_EXISTING_TOKEN', 'false').lower() == 'true'
#         if USE_EXISTING_TOKEN:
#             existing_token = os.environ.get('HUAWEI_X_SUBJECT_TOKEN')
#             token_expires = os.environ.get('HUAWEI_TOKEN_EXPIRES_AT')
            
#             if existing_token and token_expires:
#                 try:
#                     expiry_date = datetime.fromisoformat(token_expires.replace('Z', '+00:00'))
#                     if datetime.now() < expiry_date:
#                         print("✅ Using existing X-Subject-Token from environment")
#                         self.token = existing_token
#                         self.token_expires = expiry_date
#                         return self.token
#                     else:
#                         print("⚠️  Existing token has expired")
#                 except Exception as e:
#                     print(f"⚠️  Invalid token expiry format: {e}")
        
#         # If no valid existing token, use mock token for development
#         print("⚠️  No valid existing token, using mock token")
#         self.token = "mock_token_for_demo"
#         self.token_expires = datetime.now() + timedelta(hours=24)
#         return self.token
    
#     # ════════════════════════════════════════════════════════════════════════
#     # MAIN BUSINESS ADVICE FUNCTION
#     # ════════════════════════════════════════════════════════════════════════
    
#     def get_business_advice(self, 
#                        question: str, 
#                        user_context: dict = None,
#                        language: str = 'en') -> dict:
#         """Get business advice from AI or mock responses"""
        
#         USE_REAL_AI = os.environ.get('USE_REAL_AI', 'false').lower() == 'true'
        
#         if USE_REAL_AI:
#             # Use OpenRouter AI
#             print("🤖 Using OpenRouter AI")
#             return self.openrouter.get_business_advice(question, user_context, language)
#         else:
#             # Use mock responses
#             print("📝 Using mock responses")
#             return self._get_mock_response(question, user_context, language)
    
#     # ════════════════════════════════════════════════════════════════════════
#     # REAL PANGU API INTEGRATION
#     # ════════════════════════════════════════════════════════════════════════
    
#     def _call_pangu_api(self, question: str, user_context: dict, language: str) -> dict:
#         """Call real Pangu AI API"""
#         try:
#             system_prompt = self._build_system_prompt(user_context, language)
#             token = self.get_iam_token()
            
#             headers = {
#                 'Content-Type': 'application/json',
#                 'X-Auth-Token': token
#             }
            
#             # Pangu API payload format (adjust based on actual API docs)
#             payload = {
#                 'model': os.environ.get('PANGU_MODEL', 'pangu-chat-v1'),
#                 'messages': [
#                     {'role': 'system', 'content': system_prompt},
#                     {'role': 'user', 'content': question}
#                 ],
#                 'temperature': 0.7,
#                 'max_tokens': 1000,
#                 'top_p': 0.9
#             }
            
#             print(f"🤖 Calling Pangu AI API...")
            
#             response = requests.post(
#                 self.api_endpoint,
#                 headers=headers,
#                 json=payload,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
#                 print(f"✅ Pangu AI response received ({len(ai_response)} chars)")
                
#                 return {
#                     'success': True,
#                     'response': ai_response,
#                     'timestamp': datetime.now().isoformat(),
#                     'language': language,
#                     'intent': self._detect_intent(question),
#                     'suggestions': self._get_follow_up_suggestions(self._detect_intent(question), language),
#                     'source': 'pangu-ai'
#                 }
#             else:
#                 print(f"❌ Pangu API error: {response.status_code}")
#                 print(f"Response: {response.text}")
#                 return self._get_mock_response(question, user_context, language)
                
#         except Exception as e:
#             print(f"❌ Pangu API exception: {str(e)}")
#             return self._get_mock_response(question, user_context, language)
    
#     # ════════════════════════════════════════════════════════════════════════
#     # SYSTEM PROMPT BUILDER
#     # ════════════════════════════════════════════════════════════════════════
    
#     def _build_system_prompt(self, user_context: dict, language: str) -> str:
#         """Build context-aware system prompt with REAL business data"""
        
#         prompt = """You are Biz-Bantu, an expert AI business advisor for South African township solo entrepreneurs.

# TARGET AUDIENCE: Individual struggling entrepreneurs:
# - Home bakers selling vetkoek from their homes
# - Street cobblers fixing shoes under cheap gazebos
# - Seamstresses sewing clothes under trees
# - Home salon hairdressers plaiting hair at home
# - NOT spaza shop owners with bulk buying power

# MULTILINGUAL CAPABILITY (CRITICAL):
# - You MUST fluently speak English, isiZulu, Sesotho, and isiXhosa
# - Understand vernacular slang and township dialect
# - Respond in the SAME language as the question
# - Use culturally appropriate expressions

# """
        
#         # Add business identity
#         if user_context.get('businessName'):
#             business_type = user_context.get('businessType', 'business').replace('_', ' ').title()
#             prompt += f"You are advising {user_context.get('firstName', 'the owner')} who runs {user_context['businessName']}, "
#             prompt += f"a {business_type} business in {user_context.get('location', 'South Africa')}.\n\n"
        
#         # Add REAL financial data
#         if user_context.get('wallet'):
#             wallet = user_context['wallet']
#             prompt += f"""REAL FINANCIAL DATA:
# - Balance: R{wallet.get('totalBalance', 0):,.2f}
# - Cash: R{wallet.get('cashBalance', 0):,.2f}
# - Digital: R{wallet.get('digitalBalance', 0):,.2f}
# - Credit Owed: R{wallet.get('creditOwed', 0):,.2f}
# - 30-Day Sales: R{wallet.get('totalSales', 0):,.2f}
# - 30-Day Expenses: R{wallet.get('totalExpenses', 0):,.2f}

# """
        
#         # Add analytics
#         if user_context.get('analytics'):
#             analytics = user_context['analytics']
#             prompt += f"""BUSINESS ANALYTICS:
# - Daily Sales Average: R{analytics.get('averageDailySales', 0):,.2f}
# - Cash vs Digital: {analytics.get('cashVsDigital', {}).get('cashPercentage', 0):.0f}% cash
# - 30-Day Profit: R{analytics.get('incomeVsExpenses', {}).get('profit', 0):,.2f}
# - Transaction Count: {analytics.get('transactionCount', 0)}

# """
        
#         # Language instructions
#         lang_map = {'zu': 'isiZulu', 'st': 'Sesotho', 'xh': 'isiXhosa', 'en': 'English'}
#         target_lang = lang_map.get(language, 'English')
        
#         prompt += f"""RESPONSE GUIDELINES:
# 1. ALWAYS respond in {target_lang}
# 2. Use the REAL DATA above in your advice
# 3. Be specific with actual numbers
# 4. Give actionable steps for TODAY
# 5. Be encouraging but realistic
# 6. Use township-appropriate examples
# 7. Understand context of long questions

# IMPORTANT: Base ALL advice on their actual business data!
# """
        
#         return prompt
    
#     # ════════════════════════════════════════════════════════════════════════
#     # ENHANCED MOCK RESPONSES
#     # ════════════════════════════════════════════════════════════════════════
    
#     def _get_mock_response(self, question: str, user_context: dict, language: str) -> dict:
#         """
#         Production-ready mock responses with deep language understanding
#         Handles ANY question intelligently
#         """
        
#         question_lower = question.lower()
        
#         # Extract user data
#         wallet = user_context.get('wallet', {})
#         analytics = user_context.get('analytics', {})
#         credit = user_context.get('creditLedger', {})
#         first_name = user_context.get('firstName', 'friend')
#         business_name = user_context.get('businessName', 'your business')
#         business_type = user_context.get('businessType', 'BUSINESS')
        
#         total_balance = wallet.get('totalBalance', 0)
#         avg_daily_sales = analytics.get('averageDailySales', 0)
#         profit = analytics.get('incomeVsExpenses', {}).get('profit', 0)
#         outstanding_credit = credit.get('outstandingAmount', 0)
        
#         # ════════════════════════════════════════════════════════════════
#         # ADVANCED LANGUAGE DETECTION (Including Slang & Long Form)
#         # ════════════════════════════════════════════════════════════════
        
#         # isiZulu (formal + slang + long form)
#         zulu_patterns = [
#             'ngicela', 'ngifuna', 'sawubona', 'yebo', 'cha', 'ngiyabonga',
#             'angazi', 'bengifuna', 'ngingakwenza', 'kanjani', 'yini',
#             'imali', 'ibhizinisi', 'ukuthengisa', 'amakhasimende',
#             'ngi', 'u', 'si', 'ba', 'ku',  # Common prefixes
#             'ngaphansi', 'ngaphezulu', 'njalo', 'manje'  # Adverbs
#         ]
        
#         # Sesotho (formal + slang + long form)
#         sesotho_patterns = [
#             'dumela', 'ke batla', 'ke kopa', 'chelete', 'kgwebo',
#             'ho rekisa', 'bareki', 'kea leboha', 'ha ke tsebe',
#             'joang', 'eng', 'tjhelete', 'bizinese',
#             'ke', 'o', 'e', 'ba', 're',  # Common prefixes
#             'hajoale', 'kamehla', 'hape', 'haholo'  # Adverbs
#         ]
        
#         # isiXhosa (formal + slang + long form)
#         xhosa_patterns = [
#             'molo', 'ndiyafuna', 'ndicela', 'imali', 'ishishini',
#             'ukuthengisa', 'abathengi', 'enkosi', 'andazi',
#             'njani', 'yintoni', 'mali', 'ibhizinisi',
#             'ndi', 'u', 'si', 'ba', 'ku',  # Common prefixes
#             'ngoku', 'ngomso', 'izolo', 'kakhulu'  # Adverbs
#         ]
        
#         # Count language indicators
#         zu_score = sum(1 for word in zulu_patterns if word in question_lower)
#         st_score = sum(1 for word in sesotho_patterns if word in question_lower)
#         xh_score = sum(1 for word in xhosa_patterns if word in question_lower)
        
#         # Determine language (override provided language if vernacular detected)
#         if zu_score > max(st_score, xh_score) and zu_score > 0:
#             language = 'zu'
#         elif st_score > max(zu_score, xh_score) and st_score > 0:
#             language = 'st'
#         elif xh_score > max(zu_score, st_score) and xh_score > 0:
#             language = 'xh'
        
#         print(f"🗣️  Detected language: {language} (zu:{zu_score}, st:{st_score}, xh:{xh_score})")
        
#         # ════════════════════════════════════════════════════════════════
#         # INTELLIGENT INTENT DETECTION (Works across all languages)
#         # ════════════════════════════════════════════════════════════════
        
#         # Money/funding intent
#         money_keywords = [
#             # English
#             'grant', 'loan', 'funding', 'money', 'capital', 'finance', 'help', 'need',
#             # isiZulu
#             'imali', 'usizo', 'ngicela', 'ngifuna', 'ngidinga',
#             # Sesotho  
#             'chelete', 'tjhelete', 'ke batla', 'ke kopa', 'ke hloka', 'thuso',
#             # isiXhosa
#             'mali', 'uncedo', 'ndicela', 'ndifuna', 'ndidinga'
#         ]
        
#         # Sales/growth intent
#         sales_keywords = [
#             'sales', 'sell', 'customers', 'grow', 'increase', 'more', 'business',
#             'ukuthengisa', 'amakhasimende', 'khulisa', 'yandisa',
#             'ho rekisa', 'bareki', 'holisa', 'eketsa',
#             'ukuthengisa', 'abathengi', 'khulisa', 'yandisa'
#         ]
        
#         # Cash flow intent
#         cash_keywords = [
#             'cash', 'profit', 'expenses', 'balance', 'money management', 'save',
#             'izimali', 'inzuzo', 'izindleko',
#             'chelete', 'phaello', 'litjeno',
#             'imali', 'inzuzo', 'iindleko'
#         ]
        
#         # Score intent
#         score_keywords = ['score', 'credit', 'rating', 'empowerscore', 'points']
        
#         # Greeting/help intent
#         greeting_keywords = [
#             'hello', 'hi', 'hey', 'help', 'start', 'thusa',
#             'sawubona', 'sanibonani', 'dumelang', 'dumela', 'molo', 'molweni'
#         ]
        
#         # General advice/how-to intent
#         advice_keywords = [
#             'how', 'what', 'why', 'when', 'should', 'can', 'advice', 'tell me',
#             'kanjani', 'yini', 'kungani', 'nini', 'ngingakwenza',
#             'joang', 'eng', 'hobaneng', 'neng', 'nka',
#             'njani', 'yintoni', 'kutheni', 'nini', 'ndingakwenza'
#         ]
        
#         # Calculate intent scores
#         money_score = sum(1 for word in money_keywords if word in question_lower)
#         sales_score = sum(1 for word in sales_keywords if word in question_lower)
#         cash_score = sum(1 for word in cash_keywords if word in question_lower)
#         score_score = sum(1 for word in score_keywords if word in question_lower)
#         greeting_score = sum(1 for word in greeting_keywords if word in question_lower)
#         advice_score = sum(1 for word in advice_keywords if word in question_lower)
        
#         # Determine primary intent
#         intent_scores = {
#             'FUNDING': money_score,
#             'SALES': sales_score,
#             'CASH_FLOW': cash_score,
#             'SCORE': score_score,
#             'GREETING': greeting_score if len(question.split()) < 15 else 0,
#             'ADVICE': advice_score
#         }
        
#         primary_intent = max(intent_scores, key=intent_scores.get)
        
#         print(f"🎯 Intent: {primary_intent} (scores: {intent_scores})")
        
#         # ════════════════════════════════════════════════════════════════
#         # GENERATE INTELLIGENT RESPONSE
#         # ════════════════════════════════════════════════════════════════
        
#         if primary_intent == 'FUNDING' or money_score > 0:
#             response = self._generate_funding_response(
#                 first_name, business_name, business_type,
#                 total_balance, avg_daily_sales, language
#             )
        
#         elif primary_intent == 'SALES' or sales_score > 0:
#             response = self._generate_sales_response(
#                 first_name, business_name, business_type,
#                 avg_daily_sales, profit, language
#             )
        
#         elif primary_intent == 'CASH_FLOW' or cash_score > 0:
#             response = self._generate_cashflow_response(
#                 first_name, business_name, total_balance,
#                 avg_daily_sales, profit, outstanding_credit,
#                 analytics, language
#             )
        
#         elif primary_intent == 'SCORE' or score_score > 0:
#             response = self._generate_score_response(
#                 first_name, business_name, user_context,
#                 avg_daily_sales, analytics, wallet, language
#             )
        
#         elif primary_intent == 'GREETING' or (greeting_score > 0 and len(question.split()) < 15):
#             response = self._generate_greeting_response(
#                 first_name, business_name, business_type,
#                 total_balance, avg_daily_sales, profit, language
#             )
        
#         else:
#             # General advice - handles ANY other question
#             response = self._generate_general_advice(
#                 first_name, business_name, business_type,
#                 question, user_context, language
#             )
        
#         return {
#             'success': True,
#             'response': response,
#             'timestamp': datetime.now().isoformat(),
#             'language': language,
#             'intent': primary_intent,
#             'suggestions': self._get_follow_up_suggestions(primary_intent, language),
#             'usedRealData': True,
#             'dataSource': 'business_intelligence'
#         }
    
#     # ════════════════════════════════════════════════════════════════════════
#     # RESPONSE GENERATORS (One for each intent type)
#     # ════════════════════════════════════════════════════════════════════════
    
#     def _generate_funding_response(self, first_name, business_name, business_type,
#                                    total_balance, avg_daily_sales, language):
#         """Generate funding advice in chosen language"""
        
#         responses = {
#             'zu': f"""Sawubona {first_name}! 👋

# Ngibona ukuthi {business_name} inezimali ezingu-R{total_balance:,.2f}. 

# **Izindlela Zokuthola Imali:**

# 1. **NYDA Business Grant** 🎯
#    • Imali: R10,000 - R100,000
#    • Kuhle kakhulu ku-{business_type.replace('_', ' ').lower()}
#    • Isikhathi: 30 days
#    • Match: 85%

# 2. **SEFA Khula Loan** 💼
#    • Imali: R5,000 - R3,000,000
#    • Inzalo ephansi
#    • Uthengisa ngo-R{avg_daily_sales:,.2f} ngosuku - uyakwazi!

# 3. **Township Fund** 🏦
#    • Imali: R20,000 - R150,000
#    • Match: 100% - Perfect!

# 💡 **Iseluleko**: Qala nge-Township Fund ngoba ibhizinisi lakho liyakwazi ukukhokha lula.

# Ufuna usizo ngokufaka isicelo?""",
            
#             'st': f"""Dumela {first_name}! 👋

# Ke bona hore {business_name} e na le chelete ea R{total_balance:,.2f}.

# **Menyetla ea ho Fumana Chelete:**

# 1. **NYDA Business Grant** 🎯
#    • Chelete: R10,000 - R100,000
#    • E lokile bakeng sa {business_type.replace('_', ' ').lower()}
#    • Nako: 30 days
#    • Match: 85%

# 2. **SEFA Khula Loan** 💼
#    • Chelete: R5,000 - R3,000,000
#    • Mokoloto o bobebe
#    • O rekisa ka R{avg_daily_sales:,.2f} ka letsatsi - o tla khona!

# 3. **Township Fund** 🏦
#    • Chelete: R20,000 - R150,000
#    • Match: 100% - E nepahetseng!

# 💡 **Keletso**: Qala ka Township Fund hobane kgwebo ea hao e tla lefella habonolo.

# O batla thuso ho kenya kopo?""",
            
#             'xh': f"""Molo {first_name}! 👋

# Ndibona ukuba {business_name} inemali eyi-R{total_balance:,.2f}.

# **Iindlela Zokufumana Imali:**

# 1. **NYDA Business Grant** 🎯
#    • Imali: R10,000 - R100,000
#    • Ilungele {business_type.replace('_', ' ').lower()}
#    • Ixesha: 30 days
#    • Match: 85%

# 2. **SEFA Khula Loan** 💼
#    • Imali: R5,000 - R3,000,000
#    • Inzala ephantsi
#    • Uthengisa ngo-R{avg_daily_sales:,.2f} ngosuku - uya kukwazi!

# 3. **Township Fund** 🏦
#    • Imali: R20,000 - R150,000
#    • Match: 100% - Ifanelekile!

# 💡 **Icebiso**: Qala nge-Township Fund kuba ishishini lakho liza kuhlawula lula.

# Ufuna uncedo ngokufaka isicelo?""",
            
#             'en': f"""Hi {first_name}! 👋

# I see {business_name} has R{total_balance:,.2f} available.

# **Funding Options for {business_type.replace('_', ' ').title()} Businesses:**

# 1. **NYDA Business Grant** 🎯
#    • Amount: R10,000 - R100,000
#    • Perfect for solo entrepreneurs like you
#    • Deadline: 30 days
#    • Your Match: 85%

# 2. **SEFA Khula Loan** 💼
#    • Amount: R5,000 - R3,000,000
#    • Low interest rates
#    • Your R{avg_daily_sales:,.2f}/day sales qualify you!

# 3. **Township Entrepreneurship Fund** 🏦
#    • Amount: R20,000 - R150,000
#    • 100% Match - Ideal!

# 💡 **My Recommendation**: Start with Township Fund - your business can handle repayment easily.

# Want help applying?"""
#         }
        
#         return responses.get(language, responses['en'])
    
#     def _generate_sales_response(self, first_name, business_name, business_type,
#                                 avg_daily_sales, profit, language):
#         """Generate sales growth advice"""
        
#         # Get business-specific advice
#         product_advice = self._get_product_advice(business_type, language)
        
#         responses = {
#             'zu': f"""Yebo {first_name}!

# **Izindlela Zokwandisa Ukuthengisa Kwe-{business_name}:**

# 📊 **Isimo Sakho:**
# - Uthengisa: R{avg_daily_sales:,.2f} ngosuku
# - Inzuzo (30 days): R{profit:,.2f}

# 💡 **Amacebo:**

# 1. **Yandisa Uhlobo** 📦
#    {product_advice}
   
# 2. **Sebenzisa "Book"** 📓
#    • Nika amakhasimende athembekile ikhredithi
#    • Landela nge-MzansiPulse
   
# 3. **Tshela Abantu** 📢
#    • Sebenzisa WhatsApp
#    • Word of mouth is powerful!
   
# 4. **Yenza Specials** ⭐
#    • Every Friday = special offer
#    • Amakhasimende azothanda!

# Umuphi ongathanda ukuwenza kuqala?""",
            
#             'st': f"""Ee {first_name}!

# **Mekgwa ea ho Eketsa Thekiso ea {business_name}:**

# 📊 **Boemo ba Hao:**
# - O rekisa: R{avg_daily_sales:,.2f} ka letsatsi
# - Phaello (30 days): R{profit:,.2f}

# 💡 **Maele:**

# 1. **Eketsa Mefuta** 📦
#    {product_advice}
   
# 2. **Sebedisa "Book"** 📓
#    • Fa bareki bao o ba tshepang mokoloto
#    • Latela ka MzansiPulse
   
# 3. **Tsebisa Batho** 📢
#    • Sebedisa WhatsApp
#    • Puo ea molomo e matla!
   
# 4. **Etsa Li-specials** ⭐
#    • Every Friday = special offer
#    • Bareki ba tla rata!

# O ka qala ka efe?""",
            
#             'en': f"""Hi {first_name}!

# **Ways to Grow {business_name} Sales:**

# 📊 **Your Current Status:**
# - Daily Sales: R{avg_daily_sales:,.2f}
# - 30-Day Profit: R{profit:,.2f}

# 💡 **Growth Strategies:**

# 1. **Expand Your Offerings** 📦
#    {product_advice}
   
# 2. **Smart Credit** 📓
#    • Offer "book" to trusted customers
#    • Track in MzansiPulse
   
# 3. **Spread the Word** 📢
#    • Use WhatsApp groups
#    • Word of mouth is powerful!
   
# 4. **Run Specials** ⭐
#    • Weekly special offers
#    • Customers love deals!

# Which would you like to try first?"""
#         }
        
#         return responses.get(language, responses['en'])
    
#     def _generate_cashflow_response(self, first_name, business_name, total_balance,
#                                    avg_daily_sales, profit, outstanding_credit,
#                                    analytics, language):
#         """Generate cash flow management advice"""
        
#         # Determine financial health
#         if profit < 0:
#             health = "⚠️ URGENT"
#         elif profit < 500:
#             health = "⚡ Needs Work"
#         else:
#             health = "✅ Good"
        
#         # Build credit collection message if applicable
#         credit_msg_zu = ""
#         credit_msg_st = ""
#         credit_msg_en = ""
        
#         if outstanding_credit > 0:
#             credit_msg_zu = f"\n\n4. **Qoqa Ikhredithi** 💳\n   • Unezimali ezingu-R{outstanding_credit:,.2f} ezimele\n   • Collect this to improve cash flow!"
#             credit_msg_st = f"\n\n4. **Qoqa Mokoloto** 💳\n   • O na le R{outstanding_credit:,.2f} ea mokoloto\n   • Qoqa sena ho ntlafatsa phallo!"
#             credit_msg_en = f"\n\n4. **Collect Outstanding Credit** 💳\n   • You have R{outstanding_credit:,.2f} owed to you\n   • Collecting this improves cash flow!"
        
#         responses = {
#             'zu': f"""Yebo {first_name}!

# Ngibheke izimali ze-{business_name}:

# 💰 **Isimo Sakho:**
# - Imali oyinazo: R{total_balance:,.2f}
# - Uthengisa ngosuku: R{avg_daily_sales:,.2f}
# - Inzuzo (30 days): R{profit:,.2f} {health}

# **Amacebo Okwenza Kangcono:**

# 1. **Bhala Konke** 📝
#    • Log YONKE into (ngisho R5!)
#    • Consistency = better score

# 2. **Hlukanisa Imali** 💰
#    • Ungaxubi imali yebhizinisi neyakho
#    • Pay yourself a salary

# 3. **Thenga Kahle** 🛒
#    • Compare prices
#    • Buy when prices are low{credit_msg_zu}

# Ufuna usizo ngani okuthile?""",
            
#             'st': f"""Ee {first_name}!

# Ke hlahlobile lichelete tsa {business_name}:

# 💰 **Boemo ba Hao:**
# - Chelete: R{total_balance:,.2f}
# - O rekisa ka letsatsi: R{avg_daily_sales:,.2f}
# - Phaello (30 days): R{profit:,.2f} {health}

# **Maele a ho Ntlafatsa:**

# 1. **Ngola Tsohle** 📝
#    • Log EVERYTHING (esita le R5!)
#    • Consistency = score e ntle

# 2. **Arohanya Chelete** 💰
#    • Se ka khopo chelete ea kgwebo le ea hao
#    • Ipatlele moputso

# 3. **Reka Hantle** 🛒
#    • Bapisa litheko
#    • Reka ha ditheko di tlaase{credit_msg_st}

# O batla thuso ka eng?""",
            
#             'en': f"""Hi {first_name}!

# I've analyzed {business_name}'s cash flow:

# 💰 **Your Status:**
# - Balance: R{total_balance:,.2f}
# - Daily Sales: R{avg_daily_sales:,.2f}
# - 30-Day Profit: R{profit:,.2f} {health}

# **Improvement Steps:**

# 1. **Track Everything** 📝
#    • Log EVERY transaction (even R5!)
#    • Consistency builds your score

# 2. **Separate Finances** 💰
#    • Don't mix business and personal
#    • Pay yourself a salary

# 3. **Smart Purchasing** 🛒
#    • Compare supplier prices
#    • Buy in bulk when possible{credit_msg_en}

# Need help with anything specific?"""
#         }
        
#         return responses.get(language, responses['en'])
    
#     def _generate_score_response(self, first_name, business_name, user_context,
#                                 avg_daily_sales, analytics, wallet, language):
#         """Generate EmpowerScore advice"""
        
#         score = user_context.get('empowerScore', 542)
#         transaction_count = analytics.get('transactionCount', 0)
#         accuracy = wallet.get('reconciliationAccuracy', 0)
        
#         responses = {
#             'zu': f"""I-EmpowerScore Yakho: {score}/1000 🎯

# Kusukela kwi-{business_name} REAL data:

# 📊 **Izibalo Zakho:**
# - Uthengisa: R{avg_daily_sales:,.2f} ngosuku
# - Transactions: {transaction_count} (30 days)
# - Accuracy: {accuracy:.1f}%

# **Ukwenza Kangcono:**

# 1. **Consistency** (+20 points)
#    → Log yonke into nsuku zonke
#    → U-logged {transaction_count} so far!

# 2. **Reconciliation** (+15 points)
#    → Bala imali yakho every week
#    → Accuracy: {accuracy:.1f}%

# 3. **Diversify** (+10 points)
#    → Yengeza 2-3 product lines

# 🎯 **Quick Win**: Perfect week of logging = +15 points!

# Ufuna usizo ngokufinyelela PRIME tier?""",
            
#             'st': f"""EmpowerScore ea Hao: {score}/1000 🎯

# Ho tloha ho {business_name} REAL data:

# 📊 **Lipalopalo tsa Hao:**
# - O rekisa: R{avg_daily_sales:,.2f} ka letsatsi
# - Transactions: {transaction_count} (30 days)
# - Accuracy: {accuracy:.1f}%

# **Ho Ntlafatsa:**

# 1. **Consistency** (+20 points)
#    → Ngola tsohle letsatsi le letsatsi
#    → O ngodile {transaction_count} ho fihlela hona!

# 2. **Reconciliation** (+15 points)
#    → Bala chelete beke le beke
#    → Accuracy: {accuracy:.1f}%

# 3. **Diversify** (+10 points)
#    → Eketsa mefuta e 2-3

# 🎯 **Quick Win**: Beke e phethahetseng ea ho ngola = +15 points!

# O batla thuso ho fihlella PRIME tier?""",
            
#             'en': f"""Your EmpowerScore: {score}/1000 🎯

# Based on {business_name}'s REAL data:

# 📊 **Your Stats:**
# - Daily Sales: R{avg_daily_sales:,.2f}
# - Transactions: {transaction_count} (30 days)
# - Accuracy: {accuracy:.1f}%

# **How to Improve:**

# 1. **Consistency** (+20 points)
#    → Log every transaction daily
#    → You've logged {transaction_count} so far!

# 2. **Reconciliation** (+15 points)
#    → Count cash weekly
#    → Current accuracy: {accuracy:.1f}%

# 3. **Diversify** (+10 points)
#    → Add 2-3 product lines

# 🎯 **Quick Win**: Perfect week of logging = +15 points instantly!

# Want specific advice on reaching PRIME tier?"""
#         }
        
#         return responses.get(language, responses['en'])
    
#     def _generate_greeting_response(self, first_name, business_name, business_type,
#                                    total_balance, avg_daily_sales, profit, language):
#         """Generate personalized greeting"""
        
#         biz_type_friendly = business_type.replace('_', ' ').title()
        
#         responses = {
#             'zu': f"""Sawubona {first_name}! 👋

# Ngingu **Biz-Bantu**, futhi nginolwazi nge-{business_name}!

# 📊 **Izibalo Zakho:**
# - Imali: R{total_balance:,.2f}
# - Uthengisa ngosuku: R{avg_daily_sales:,.2f}
# - Inzuzo (30 days): R{profit:,.2f}

# Ngingakusiza nge:

# 💰 Ukuthola imali (ngokubheka YAKHO data)
# 📈 Ukwandisa ukuthengisa kwe-{biz_type_friendly}
# 📊 Ukulawula imali
# 🎯 Ukwenza i-EmpowerScore ibe ngcono

# **Ngikhuluma isiZulu, Sesotho, isiXhosa ne-English!**

# Ungathanda usizo ngani namhlanje?""",
            
#             'st': f"""Dumela {first_name}! 👋

# Ke **Biz-Bantu**, mme ke na le tlhahisoleseding ea {business_name}!

# 📊 **Lipalopalo tsa Hao:**
# - Chelete: R{total_balance:,.2f}
# - O rekisa ka letsatsi: R{avg_daily_sales:,.2f}
# - Phaello (30 days): R{profit:,.2f}

# Nka o thusa ka:

# 💰 Ho fumana chelete (ho latela EA HAO data)
# 📈 Ho eketsa thekiso ea {biz_type_friendly}
# 📊 Ho laola chelete
# 🎯 Ho ntlafatsa EmpowerScore

# **Ke bua Sesotho, isiZulu, isiXhosa le English!**

# O batla thuso ka eng kajeno?""",
            
#             'xh': f"""Molo {first_name}! 👋

# Ndigu **Biz-Bantu**, kwaye ndinolwazi nge-{business_name}!

# 📊 **Iinkcukacha Zakho:**
# - Imali: R{total_balance:,.2f}
# - Uthengisa ngosuku: R{avg_daily_sales:,.2f}
# - Inzuzo (30 days): R{profit:,.2f}

# Ndingakunceda nge:

# 💰 Ukufumana imali (ngokubheka EYAKHO data)
# 📈 Ukukhulisa intengiso ye-{biz_type_friendly}
# 📊 Ukulawula imali
# 🎯 Ukuphucula i-EmpowerScore

# **Ndithetha isiXhosa, isiZulu, Sesotho kunye ne-English!**

# Ufuna uncedo ngantoni namhlanje?""",
            
#             'en': f"""Hello {first_name}! 👋

# I'm **Biz-Bantu**, and I have access to {business_name}'s real data!

# 📊 **Your Quick Stats:**
# - Balance: R{total_balance:,.2f}
# - Daily Sales: R{avg_daily_sales:,.2f}
# - 30-Day Profit: R{profit:,.2f}

# I can help with:

# 💰 Finding funding (based on YOUR data)
# 📈 Growing your {biz_type_friendly} business
# 📊 Managing cash flow
# 🎯 Improving your EmpowerScore

# **I speak isiZulu, Sesotho, isiXhosa, and English!**

# What do you need help with today?"""
#         }
        
#         return responses.get(language, responses['en'])
    
#     def _generate_general_advice(self, first_name, business_name, business_type,
#                                 question, user_context, language):
#         """Handle ANY other question intelligently"""
        
#         question_lower = question.lower()
        
#         # Determine topic
#         if any(word in question_lower for word in ['customer', 'client', 'amakhasimende', 'bareki', 'abathengi']):
#             topic = 'customers'
#         elif any(word in question_lower for word in ['product', 'stock', 'inventory', 'thepa', 'into']):
#             topic = 'products'
#         elif any(word in question_lower for word in ['competition', 'competitor', 'rival', 'other']):
#             topic = 'competition'
#         elif any(word in question_lower for word in ['market', 'advertise', 'promote', 'brand']):
#             topic = 'marketing'
#         elif any(word in question_lower for word in ['staff', 'employee', 'hire', 'worker', 'help']):
#             topic = 'staffing'
#         elif any(word in question_lower for word in ['location', 'place', 'where', 'move', 'indawo']):
#             topic = 'location'
#         elif any(word in question_lower for word in ['time', 'hour', 'when', 'schedule', 'isikhathi', 'nako']):
#             topic = 'time'
#         else:
#             topic = 'general'
        
#         print(f"🤔 General advice topic: {topic}")
        
#         responses = {
#             'zu': f"""Yebo {first_name}!

# Umbuzo wakho nge-{topic} we-{business_name}...

# Ngokubheka izibalo zakho:
# - Uthengisa R{user_context.get('analytics', {}).get('averageDailySales', 0):,.2f} ngosuku
# - Business type: {business_type.replace('_', ' ').lower()}

# Ngingakusiza kahle! Ungabuza:

# 💡 Iseluleko ngokukhiqiza izinto ezintsha
# 💡 Kanjani ngikhetha indawo engcono
# 💡 Amacebo okunakekelwa kwamakhasimende

# Yimuphi umbuzo ocacile ongiwuzayo?""",
            
#             'st': f"""Ee {first_name}!

# Potso ea hao ka {topic} ea {business_name}...

# Ho latela lipalo tsa hao:
# - O rekisa R{user_context.get('analytics', {}).get('averageDailySales', 0):,.2f} ka letsatsi
# - Business type: {business_type.replace('_', ' ').lower()}

# Nka o thusa! O ka botsa:

# 💡 Keletso ea ho etsa thepa e ncha
# 💡 Joang ho khetha sebaka se molemo
# 💡 Maele a ho sebeletsa bareki

# Ke potso efe e hlakileng?""",
            
#             'en': f"""Hi {first_name}!

# Your question about {topic} for {business_name}...

# Based on your stats:
# - Daily Sales: R{user_context.get('analytics', {}).get('averageDailySales', 0):,.2f}
# - Business Type: {business_type.replace('_', ' ').title()}

# I can help! Ask me:

# 💡 How to add new products/services
# 💡 Best practices for customer service
# 💡 Tips on choosing a better location

# What specific aspect would you like advice on?"""
#         }
        
#         return responses.get(language, responses['en'])
    
#     # ════════════════════════════════════════════════════════════════════════
#     # HELPER FUNCTIONS
#     # ════════════════════════════════════════════════════════════════════════
    
#     def _get_product_advice(self, business_type: str, language: str) -> str:
#         """Get business-type specific product advice"""
        
#         advice_map = {
#             'HOME_BAKER': {
#                 'zu': 'Yengeza amagwinya, amaqebhulengwane, amakuku',
#                 'st': 'Eketsa makobo, liaparo, dikuku',
#                 'xh': 'Yongeza iinkukhu, amaqebhulengwane, iikuku',
#                 'en': 'Add vetkoek, scones, birthday cakes'
#             },
#             'SHOE_REPAIR': {
#                 'zu': 'Thengisa amashoelace, i-polish, amasocks',
#                 'st': 'Rekisa dikhoele, polish, likgarebe',
#                 'xh': 'Thengisa izintambo, ipolishi, iisokisi',
#                 'en': 'Sell shoelaces, polish, socks'
#             },
#             'HOME_SALON': {
#                 'zu': 'Yengeza i-makeup, izinzipho, izinwele',
#                 'st': 'Eketsa makeup, dinala, moriri',
#                 'xh': 'Yongeza i-makeup, iinzipho, iinwele',
#                 'en': 'Add makeup, nails, hair extensions'
#             },
#             'SEAMSTRESS': {
#                 'zu': 'Yengeza ukushonisa, ama-zip, ukubazisa',
#                 'st': 'Eketsa ho ruruha, di-zip, ho sekisa',
#                 'xh': 'Yongeza ukuthunga, ii-zip, ukulungisa',
#                 'en': 'Add mending, zippers, alterations'
#             },
#             'CAR_WASH': {
#                 'zu': 'Yengeza i-wax, interior cleaning, polish',
#                 'st': 'Eketsa wax, ho hloekisa ka hare, polish',
#                 'xh': 'Yongeza i-wax, ukucoceka ngaphakathi, polish',
#                 'en': 'Add waxing, interior detailing, polish'
#             }
#         }
        
#         advice = advice_map.get(business_type, {})
#         return advice.get(language, advice.get('en', 'Diversify your offerings'))
    
#     def _detect_intent(self, question: str) -> str:
#         """Simplified intent detection"""
#         question_lower = question.lower()
        
#         if any(word in question_lower for word in ['grant', 'loan', 'funding', 'imali', 'chelete', 'mali']):
#             return 'FUNDING_INQUIRY'
#         elif any(word in question_lower for word in ['sales', 'sell', 'customers', 'ukuthengisa', 'ho rekisa']):
#             return 'SALES_ADVICE'
#         elif any(word in question_lower for word in ['cash', 'profit', 'expenses', 'balance']):
#             return 'FINANCIAL_ADVICE'
#         elif any(word in question_lower for word in ['score', 'credit', 'rating']):
#             return 'SCORE_INQUIRY'
#         else:
#             return 'GENERAL_INQUIRY'
    
#     def _get_follow_up_suggestions(self, intent: str, language: str) -> list:
#         """Get context-aware follow-up suggestions"""
        
#         suggestions_map = {
#             'FUNDING': {
#                 'zu': ["Yimuphi i-grant engifanele?", "Ngingakwenza kanjani ngibe better?", "Ngidinga maphi amaphepha?"],
#                 'st': ["Ke grant efe eo nka e kenyang?", "Nka ntlafatsa joang monyetla?", "Ke hloka litokomane life?"],
#                 'xh': ["Ngowuphi umxhaso endingawufaka?", "Ndingayenza njani ibe ngcono?", "Ndidinga amaxwebhu aphi?"],
#                 'en': ["Which grant should I apply for?", "How do I improve my chances?", "What documents do I need?"]
#             },
#             'SALES': {
#                 'zu': ["Ngingakhanga kanjani amakhasimende?", "Ngingapha ikhredithi?", "Yini ethengiseka kahle?"],
#                 'st': ["Nka hohela bareki ba batjha joang?", "Nka fa mokoloto?", "Ke eng e rekiswang hantle?"],
#                 'xh': ["Ndingatsala njani abathengi abatsha?", "Ndinganika ityala?", "Yintoni ethengiswa kakuhle?"],
#                 'en': ["How do I attract more customers?", "Should I offer credit?", "What sells best?"]
#             },
#             'FINANCIAL_ADVICE': {
#                 'zu': ["Nginganciphisa kanjani izindleko?", "Ngingaqasha abantu?", "Inzuzo enkulu?"],
#                 'st': ["Nka fokotsa joang litjeno?", "Nka hira batho?", "Phaello e ntle?"],
#                 'xh': ["Ndinganciphisa njani iindleko?", "Ndingaqesha abantu?", "Yimalini enzuzo?"],
#                 'en': ["How can I reduce costs?", "Should I hire staff?", "What's good profit?"]
#             },
#             'SCORE_INQUIRY': {
#                 'zu': ["Ngingafinyelela kanjani PRIME?", "Yini elimaza i-score?", "Kuthatha isikhathi esingakanani?"],
#                 'st': ["Nka fihlella joang PRIME?", "Ke eng e senyang score?", "E nka nako e kae?"],
#                 'xh': ["Ndingafikelela njani PRIME?", "Yintoni emonakalisa i-score?", "Kuthatha ixesha elingakanani?"],
#                 'en': ["How can I reach PRIME tier?", "What hurts my score?", "How long to improve?"]
#             },
#             'GREETING': {
#                 'zu': ["Ngitshele nge-grants", "Ngingakwandisa kanjani ukuthengisa?", "I-EmpowerScore yami?"],
#                 'st': ["Mpolelele ka li-grants", "Nka eketsa joang thekiso?", "EmpowerScore ea ka?"],
#                 'xh': ["Ndixelele nge-grants", "Ndingayandisa njani intengiso?", "I-EmpowerScore yam?"],
#                 'en': ["Tell me about grants", "How to grow sales?", "What's my EmpowerScore?"]
#             },
#             'GENERAL_INQUIRY': {
#                 'zu': ["Ngingakhulisa kanjani ibhizinisi?", "Ngitshengise izindlela zemali", "Amacebo okulawula"],
#                 'st': ["Nka holisa joang kgwebo?", "Ntshupeha menyetla ea chelete", "Maele a ho laola"],
#                 'xh': ["Ndingalikhulisa njani ishishini?", "Ndibonise iindlela zemali", "Amacebiso okulawula"],
#                 'en': ["How can I grow my business?", "Show me funding options", "Cash management tips"]
#             }
#         }
        
#         suggestions = suggestions_map.get(intent, suggestions_map['GENERAL_INQUIRY'])
#         return suggestions.get(language, suggestions['en'])


# # ════════════════════════════════════════════════════════════════════════════
# # TEST FUNCTION
# # ════════════════════════════════════════════════════════════════════════════

# if __name__ == "__main__":
#     """Test enhanced multilingual responses"""
    
#     print("=" * 80)
#     print("🤖 Testing Enhanced Biz-Bantu AI Helper")
#     print("=" * 80)
    
#     pangu = PanguAIHelper(
#         project_id="demo-project",
#         access_key="demo-ak",
#         secret_key="demo-sk"
#     )
    
#     # Test with realistic context
#     user_context = {
#         'firstName': 'Nthabiseng',
#         'businessName': 'Ausi Nthabiseng Home Bakery',
#         'businessType': 'HOME_BAKER',
#         'location': 'Soweto, Gauteng',
#         'empowerScore': 542,
#         'wallet': {
#             'totalBalance': 1250.00,
#             'cashBalance': 1200.00,
#             'digitalBalance': 50.00,
#             'creditOwed': 300.00
#         },
#         'analytics': {
#             'averageDailySales': 187.50,
#             'transactionCount': 45,
#             'incomeVsExpenses': {
#                 'profit': 850.00
#             }
#         }
#     }
    
#     # Test questions
#     test_questions = [
#         ("Dumela", "st"),
#         ("Sawubona ngicela usizo", "zu"),
#         ("Ke nyulosa chelete ea kgwebo joang", "st"),
#         ("How can I compete with other bakeries?", "en"),
#     ]
    
#     for question, lang in test_questions:
#         print(f"\n{'='*80}")
#         print(f"❓ Question: {question}")
#         print(f"🗣️  Language: {lang}")
#         print(f"{'='*80}")
        
#         response = pangu.get_business_advice(question, user_context, lang)
        
#         print(f"\n💬 Response:\n{response['response']}")
#         print(f"\n💡 Suggestions: {', '.join(response['suggestions'][:2])}")
#         print(f"🎯 Intent: {response['intent']}")
    
#     print("\n" + "=" * 80)
#     print("✅ Enhanced Multilingual AI Test Complete!")
#     print("=" * 80)

"""
Pangu AI Helper - Condensed Production Version
Uses OpenRouter AI for intelligent responses
"""

import os
from datetime import datetime, timedelta
from openrouter_helper import OpenRouterHelper

class PanguAIHelper:
    """
    Helper class for AI-powered business advice
    Delegates to OpenRouter for real AI responses
    """
    
    def __init__(self, project_id: str, access_key: str, secret_key: str, region: str = 'af-south-1'):
        """Initialize AI helper"""
        self.project_id = project_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        
        # Initialize OpenRouter for real AI
        self.openrouter = OpenRouterHelper()
        
        print(f"🤖 Pangu AI Helper initialized")
    
    def get_business_advice(self, 
                           question: str, 
                           user_context: dict = None,
                           language: str = 'en') -> dict:
        """
        Get business advice using OpenRouter AI
        
        Args:
            question: User's question
            user_context: Business context with real data
            language: Preferred language (en, zu, st, xh)
            
        Returns:
            dict: AI response with suggestions
        """
        
        USE_REAL_AI = os.environ.get('USE_REAL_AI', 'true').lower() == 'true'

        if USE_REAL_AI:
            # Use OpenRouter AI (REAL INTELLIGENT RESPONSES)
            print("🤖 Using OpenRouter AI")
            try:
                return self.openrouter.get_business_advice(question, user_context, language)
            except Exception as e:
                print(f"❌ OpenRouter failed: {e}, falling back to basic response")
                return self._get_fallback_response(question, user_context, language)
        else:
            # Use basic fallback (when AI is disabled)
            print("📝 Using fallback responses")
            return self._get_fallback_response(question, user_context, language)
    
    def _get_fallback_response(self, question: str, user_context: dict, language: str) -> dict:
        """
        Simple fallback when AI is unavailable
        Just acknowledges the question and suggests enabling AI
        """
        
        first_name = user_context.get('firstName', 'friend')
        
        fallback_messages = {
            'en': f"""Hi {first_name}! 👋

I'm Biz-Bantu, your AI business advisor. I can help you with:
- Finding funding and grants
- Growing your sales
- Managing cash flow
- Improving your EmpowerScore

To get personalized advice based on your real business data, please enable AI mode in settings.

What would you like to know?""",
            
            'zu': f"""Sawubona {first_name}! 👋

Ngingu Biz-Bantu, umseluleki wakho webhizinisi. Ngingakusiza nge:
- Ukuthola imali ne-grants
- Ukukhulisa ukuthengisa
- Ukulawula imali
- Ukwenza i-EmpowerScore ibe ngcono

Ungathanda usizo ngani?""",
            
            'st': f"""Dumela {first_name}! 👋

Ke Biz-Bantu, molekgotla oa hao oa kgwebo. Nka o thusa ka:
- Ho fumana chelete le li-grants
- Ho holisa thekiso
- Ho laola chelete
- Ho ntlafatsa EmpowerScore

O batla thuso ka eng?""",
            
            'xh': f"""Molo {first_name}! 👋

NdinguBiz-Bantu, umcebisi wakho weshishini. Ndingakunceda nge:
- Ukufumana imali ne-grants
- Ukukhulisa intengiso
- Ukulawula imali
- Ukuphucula i-EmpowerScore

Ufuna uncedo ngantoni?"""
        }
        
        response = fallback_messages.get(language, fallback_messages['en'])
        
        return {
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'language': language,
            'intent': 'GENERAL_INQUIRY',
            'suggestions': self._get_basic_suggestions(language),
            'usedRealData': False,
            'dataSource': 'fallback'
        }
    
    def _get_basic_suggestions(self, language: str) -> list:
        """Get basic follow-up suggestions"""
        
        suggestions = {
            'en': ["Tell me about grants", "How to grow sales?", "What's my balance?"],
            'zu': ["Ngitshele nge-grants", "Ngingakwandisa ukuthengisa?", "Imali yami?"],
            'st': ["Mpolelele ka grants", "Nka eketsa thekiso?", "Chelete ea ka?"],
            'xh': ["Ndixelele nge-grants", "Ndingayandisa intengiso?", "Imali yam?"]
        }
        
        return suggestions.get(language, suggestions['en'])


# ════════════════════════════════════════════════════════════════════════════
# TEST FUNCTION
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test AI integration"""
    
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 80)
    print("🤖 Testing Condensed Biz-Bantu AI Helper")
    print("=" * 80)
    
    ai = PanguAIHelper(
        project_id="demo-project",
        access_key="demo-ak",
        secret_key="demo-sk"
    )
    
    # Test context
    user_context = {
        'firstName': 'Lerato',
        'businessName': 'Lerato Home Salon',
        'businessType': 'HOME_SALON',
        'location': 'Orange Farm, Gauteng',
        'wallet': {
            'totalBalance': 2500.00,
            'cashBalance': 2300.00,
            'digitalBalance': 200.00,
        },
        'analytics': {
            'averageDailySales': 350.00,
            'transactionCount': 67,
            'incomeVsExpenses': {'profit': 1200.00}
        }
    }
    
    # Test question
    response = ai.get_business_advice(
        "How can I grow my salon business?",
        user_context,
        'en'
    )
    
    if response['success']:
        print(f"\n✅ Response received ({len(response['response'])} chars)")
        print(f"🤖 Source: {response.get('dataSource', 'unknown')}")
        print(f"\n💬 Preview:\n{response['response'][:200]}...")
    else:
        print(f"\n❌ Error: {response.get('error')}")
    
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    